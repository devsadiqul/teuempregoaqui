import time
import requests
from django.conf import settings

DEFAULTS = {
    "TOKEN_URL": "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
    "BASE_URL": "https://api.francetravail.io",
    "SEARCH_PATH": "/partenaire/offresdemploi/v2/offres/search",
    "SCOPE": "api_offresdemploiv2 o2dsoffre",
}


def _cfg(key):
    conf = getattr(settings, "FRANCE_TRAVAIL", {})
    return conf.get(key, DEFAULTS.get(key))


class FranceTravailAuth:
    
    def __init__(self):
        self._token = None
        self._expires_at = 0.0

    def token(self) -> str:
        if self._token and time.time() < self._expires_at - 30:
            return self._token
        resp = requests.post(
            _cfg("TOKEN_URL"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": _cfg("CLIENT_ID"),
                "client_secret": _cfg("CLIENT_SECRET"),
                "scope": _cfg("SCOPE"),
            },
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._expires_at = time.time() + int(payload.get("expires_in", 1200))
        return self._token


class OffresClient:

    def __init__(self, auth: FranceTravailAuth = None):
        self.auth = auth or FranceTravailAuth()

    def search(self, *, code_rome=None, mots_cles=None, commune=None,
               departement=None, range_start=0, range_end=49, **extra) -> dict:

        params = {k: v for k, v in {
            "codeROME": code_rome,
            "motsCles": mots_cles,
            "commune": commune,
            "departement": departement,
            "range": f"{range_start}-{range_end}",
            **extra,
        }.items() if v is not None}

        url = _cfg("BASE_URL") + _cfg("SEARCH_PATH")
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.auth.token()}",
                     "Accept": "application/json"},
            params=params, timeout=20,
        )
        if resp.status_code == 204:
            return {"offres": [], "total": 0}
        resp.raise_for_status()
        data = resp.json()

        total = None
        cr = resp.headers.get("Content-Range", "")
        if "/" in cr:
            try:
                total = int(cr.rsplit("/", 1)[-1])
            except ValueError:
                total = None
        return {"offres": data.get("resultats", []), "total": total}
