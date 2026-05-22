import httpx
from app.config import settings
from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.status import CheckStatus

class BgpVisibilityService:
    def __init__(self, client): self.client=client

    def _ripestat(self,prefix):
        payload,diag=self.client.get_with_diagnostics('routing-status',{'resource':prefix})
        data=(payload or {}).get('data',{}) if isinstance(payload,dict) else {}
        origins=sorted({str(i.get('origin','')).upper() for i in data.get('routes',[]) if isinstance(i,dict) and i.get('origin')})
        return {'source':'ripestat','origins':origins,'visible':bool(origins),'diagnostic':diag,'ok':not (payload or {}).get('error')}

    def _generic(self,prefix):
        tpl=settings.bgp_generic_url_template
        if not tpl: return {'source':'generic-http','origins':[],'visible':False,'diagnostic':{'source':'generic-http','status':'error','message':'template missing'},'ok':False}
        try:
            r=httpx.get(tpl.format(prefix=prefix),timeout=settings.bgp_provider_timeout_seconds); r.raise_for_status(); j=r.json()
            origins=[str(x).upper() for x in (j.get('origins') or []) if x]
            visible=bool(j.get('visible', bool(origins)))
            return {'source':'generic-http','origins':origins,'visible':visible,'diagnostic':{'source':'generic-http','status':'ok'},'ok':True,'raw':j}
        except Exception as exc:
            return {'source':'generic-http','origins':[],'visible':False,'diagnostic':{'source':'generic-http','status':'error','message':str(exc)},'ok':False}

    def check(self,prefix,expected_origin_as):
        p=validate_prefix(prefix); exp=format_asn(normalize_asn(expected_origin_as)) if expected_origin_as else None
        providers=[x.strip() for x in settings.bgp_visibility_providers.split(',') if x.strip()]
        results=[]
        for pr in providers:
            if pr=='ripestat': results.append(self._ripestat(p))
            elif pr=='generic-http': results.append(self._generic(p))
        by={r['source']:r['origins'] for r in results}
        all_orig=sorted({o for r in results for o in r['origins']})
        exp_by={r['source']:(exp in r['origins'] if exp else None) for r in results}
        miss=[s for s,v in exp_by.items() if v is False]
        conflicting=sorted([o for o in all_orig if exp and o!=exp])
        succ=sum(1 for r in results if r.get('ok')); fail=len(results)-succ
        agreement=len(set(tuple(r['origins']) for r in results if r.get('ok')))<=1 if succ>1 else True
        conf=100 if succ==0 else int((sum(1 for v in exp_by.values() if v is True)/max(1,succ))*100) if exp else int((succ/max(1,len(results)))*100)
        if succ==0: status=CheckStatus.UNKNOWN.value; summary='No BGP visibility source returned usable data.'
        elif exp and any(v is False for v in exp_by.values()): status=CheckStatus.CRITICAL.value if succ==1 else CheckStatus.WARNING.value; summary='Expected origin is missing on at least one source.'
        elif conflicting or (not exp and len(all_orig)>1): status=CheckStatus.WARNING.value; summary='Conflicting origin ASNs observed across sources.'
        else: status=CheckStatus.OK.value; summary='BGP visibility is consistent for expected origin.'
        return {"status":status,"summary":summary,"explanation":"Aggregated multi-source BGP visibility.","risk":"External routing views can be delayed or partial.","recommendations":["Investigate source disagreements before change execution."],"input":{"prefix":p,"expected_origin_as":exp},"checks":None,"details":{"prefix":p,"visible_origins_by_source":by,"all_visible_origins":all_orig,"expected_origin_seen_by_source":exp_by,"conflicting_origins":conflicting,"missing_expected_origin_sources":miss,"source_agreement":agreement,"confidence_score":conf,"source_diagnostics":[r.get('diagnostic') for r in results],"provider_count":len(results),"successful_provider_count":succ,"failed_provider_count":fail},"sources":providers}
