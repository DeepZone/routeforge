import httpx
import ipaddress, json
from pathlib import Path
from app.config import settings
from app.core.normalize import normalize_asn
from app.core.status import CheckStatus


def _to_status(v: str|None):
    m={"valid":CheckStatus.OK.value,"invalid_asn":CheckStatus.CRITICAL.value,"invalid_length":CheckStatus.CRITICAL.value,"not_found":CheckStatus.WARNING.value,None:CheckStatus.UNKNOWN.value}
    return m.get(v, CheckStatus.UNKNOWN.value)

class RpkiProviderService:
    def __init__(self, client): self.client=client
    def check(self,prefix:str,origin_as:str|None)->dict:
        if not origin_as:
            return {"provider":settings.rpki_provider,"provider_status":"skipped","validation_status":None,"status":CheckStatus.UNKNOWN.value,"summary":"No origin AS provided for RPKI validation.","matched_roas":[],"checked_prefix":prefix,"checked_origin_as":None,"fallback_used":False,"fallback_reason":None,"source_diagnostics":[],"raw":{}}
        provider=(settings.rpki_provider or "ripestat").lower()
        if provider=="ripestat":
            return self._ripestat(prefix,origin_as)
        primary = self._routinator if provider=="routinator" else self._local_json if provider=="local-json" else self._auto
        return primary(prefix,origin_as)
    def _auto(self,prefix,origin_as):
        diags=[]
        local=self._routinator(prefix,origin_as)
        diags.extend(local.get('source_diagnostics',[]))
        if local.get('provider_status')=='ok':
            fallback=self._ripestat(prefix,origin_as)
            disagree=fallback.get('validation_status')!=local.get('validation_status')
            local['provider_disagreement']=disagree
            if disagree: diags.append({'source':'provider_agreement','status':'warning','message':'local vs RIPEstat disagreement'})
            local['source_diagnostics']=diags
            return local
        if settings.rpki_fallback_to_ripestat:
            fb=self._ripestat(prefix,origin_as); fb['fallback_used']=True; fb['fallback_reason']='local provider failed'; fb['source_diagnostics']=diags+fb.get('source_diagnostics',[]); return fb
        local['status']=CheckStatus.UNKNOWN.value; return local
    def _ripestat(self,prefix,origin_as):
        asn=normalize_asn(origin_as); p=self.client.get('rpki-validation',{'resource':str(asn),'prefix':prefix}) or {}
        v=(p.get('data',{}) if isinstance(p,dict) else {}).get('status')
        return {"provider":"ripestat","provider_status":"ok" if not p.get('error') else 'error',"validation_status":v,"status":_to_status(v),"summary":f"RPKI validation via RIPEstat: {v or 'unknown'}","matched_roas":(p.get('data',{}) if isinstance(p,dict) else {}).get('validating_roas',[]),"checked_prefix":prefix,"checked_origin_as":f"AS{asn}","fallback_used":False,"fallback_reason":None,"source_diagnostics":[],"raw":p}
    def _routinator(self,prefix,origin_as):
        url=settings.rpki_routinator_url.rstrip('/')+'/api/v1/validity/'+origin_as.replace('AS','')+'/'+prefix
        try:
            r=httpx.get(url,timeout=settings.rpki_provider_timeout_seconds); r.raise_for_status(); j=r.json();
            st=j.get('validated_route',{}).get('validity',{}).get('state') or j.get('state')
            mapped={'valid':'valid','invalid':'invalid_asn','not-found':'not_found'}.get(st,st)
            return {"provider":"routinator","provider_status":"ok","validation_status":mapped,"status":_to_status(mapped),"summary":f"RPKI validation via Routinator: {mapped or 'unknown'}","matched_roas":j.get('validated_route',{}).get('VRPs',[]) or j.get('vrps',[]),"checked_prefix":prefix,"checked_origin_as":origin_as,"fallback_used":False,"fallback_reason":None,"source_diagnostics":[],"raw":j}
        except Exception as exc:
            return {"provider":"routinator","provider_status":"error","validation_status":None,"status":CheckStatus.UNKNOWN.value,"summary":"Routinator unavailable","matched_roas":[],"checked_prefix":prefix,"checked_origin_as":origin_as,"fallback_used":False,"fallback_reason":None,"source_diagnostics":[{"source":"routinator","status":"error","message":str(exc)}],"raw":{}}
    def _local_json(self,prefix,origin_as):
        try:
            entries=json.loads(Path(settings.rpki_local_json_path).read_text())
            net=ipaddress.ip_network(prefix,strict=False); asn=normalize_asn(origin_as)
            matches=[]
            for e in entries if isinstance(entries,list) else entries.get('roas',[]):
                pfx=e.get('prefix') or e.get('asn_prefix')
                if not pfx: continue
                roanet=ipaddress.ip_network(pfx,strict=False)
                if net.subnet_of(roanet):
                    mlen=int(e.get('maxLength',e.get('max_length',roanet.prefixlen)))
                    easn=str(e.get('asn','')).upper().replace('AS','')
                    if easn==str(asn) and net.prefixlen<=mlen: matches.append(e)
            val='valid' if matches else 'not_found'
            return {"provider":"local-json","provider_status":"ok","validation_status":val,"status":_to_status(val),"summary":f"RPKI validation via local JSON: {val}","matched_roas":matches,"checked_prefix":prefix,"checked_origin_as":origin_as,"fallback_used":False,"fallback_reason":None,"source_diagnostics":[],"raw":{}}
        except Exception as exc:
            return {"provider":"local-json","provider_status":"error","validation_status":None,"status":CheckStatus.UNKNOWN.value,"summary":"Local JSON validator unavailable","matched_roas":[],"checked_prefix":prefix,"checked_origin_as":origin_as,"fallback_used":False,"fallback_reason":None,"source_diagnostics":[{"source":"local-json","status":"error","message":str(exc)}],"raw":{}}
