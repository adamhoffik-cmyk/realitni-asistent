# Google OAuth Setup — Calendar + Drive

Pro napojení kalendáře a Drive potřebuješ vlastní OAuth Client v Google Cloud Console. Je to **zdarma** a trvá ~10 min.

## Krok 1 — Google Cloud Console project

1. Jdi na [console.cloud.google.com](https://console.cloud.google.com/)
2. Nahoře klikni **"Select a project"** → **"NEW PROJECT"**
3. Name: `Realitni Asistent`
4. Create

## Krok 2 — Povol APIs

1. V menu vlevo: **APIs & Services → Library**
2. Najdi a **Enable** tyto APIs:
   - **Google Calendar API**
   - **Google Drive API**

## Krok 3 — OAuth consent screen

1. **APIs & Services → OAuth consent screen**
2. User Type: **External** (protože používáš osobní Gmail, ne Google Workspace) → Create
3. Vyplň:
   - App name: `Realitní Asistent`
   - User support email: `adam.hoffik@gmail.com`
   - Developer contact: `adam.hoffik@gmail.com`
4. **Save and Continue**
5. Scopes: přidej přes **"Add or Remove Scopes"**:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/drive.file`
6. **Save and Continue**
7. Test users: přidej `adam.hoffik@gmail.com` (jen ten se smí přihlašovat dokud je app v testovacím módu — což stačí, publishing není potřeba)
8. **Save and Continue** → Back to Dashboard

## Krok 4 — OAuth Client ID

1. **APIs & Services → Credentials**
2. **Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Name: `Asistent Backend`
5. **Authorized redirect URIs** — přidej:
   ```
   https://asistent.46-225-58-232.nip.io/api/auth/google/callback
   ```
6. **Create** — dostaneš `Client ID` a `Client Secret`. Stáhni JSON nebo zkopíruj obě hodnoty.

## Krok 5 — Vlož do `.env` na VPS

```bash
ssh root@46.225.58.232
cd /opt/realitni-asistent

# Uprav .env — najdi tyto řádky a vyplň:
nano .env
```

```env
GOOGLE_CLIENT_ID=xxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
GOOGLE_REDIRECT_URI=https://asistent.46-225-58-232.nip.io/api/auth/google/callback
```

Po úpravě:
```bash
docker compose --profile production restart backend
```

## Krok 6 — Propojit Google účet v aplikaci

1. Otevři https://asistent.46-225-58-232.nip.io
2. V kalendář widgetu klikni **"Připojit Google účet"**
3. Prohlížeč tě přesměruje na Google consent screen
4. Přihlas se jako `adam.hoffik@gmail.com` a povol všechny scopy
5. Po úspěchu se vrátíš na "✓ Google připojen" stránku
6. Zpět na home → kalendář už ukazuje tvé události

## Troubleshooting

### "This app isn't verified"
Během testovacího módu Google ukáže varování. Klikni **"Advanced" → "Go to Realitní Asistent (unsafe)"** — je to normální pro tvou osobní app.

### "redirect_uri_mismatch"
Redirect URI v Google Console MUSÍ přesně odpovídat `GOOGLE_REDIRECT_URI` v `.env`. Zkontroluj https vs http, trailing slash.

### Tokeny expirovaly
Backend si access token automaticky refreshuje přes refresh token. Pokud bys chtěl revoke, zavolej:
```bash
curl -u adam:HESLO -X POST https://asistent.46-225-58-232.nip.io/api/auth/google/revoke
```

## Odvolání přístupu

- V Google: [myaccount.google.com/permissions](https://myaccount.google.com/permissions) → Realitní Asistent → Remove access
- V aplikaci: `POST /api/auth/google/revoke` (viz výše)
