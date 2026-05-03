# varenphangkajaya.com — Portfolio

## Files
- `index.html` — main website
- `admin/` — Netlify CMS admin panel
- `netlify.toml` — Netlify config
- `images/` — upload your photos here (or via /admin)

## Deploy Steps

### 1. Upload to GitHub
- Create new repo: `varen-portfolio`
- Upload all files

### 2. Connect to Netlify
- Go to netlify.com → Add new site → Import from Git
- Select your repo
- Build command: leave empty
- Publish directory: `.`
- Deploy site

### 3. Enable Netlify Identity + Git Gateway
- Netlify dashboard → Site settings → Identity → Enable
- Identity → Services → Git Gateway → Enable
- Identity → Registration → Invite only

### 4. Invite yourself
- Identity → Invite users → varenphangkajaya@gmail.com

### 5. Add custom domain
- Netlify → Domain management → Add domain → varenphangkajaya.com

### 6. Access CMS
- Go to varenphangkajaya.com/admin
- Login with your email
- Upload photos, edit text per section

## CMS Fields Per Section

| Section | Fields |
|---|---|
| Homepage | 3 hero photos (one per track) |
| Campaign Production | Cover + 6 campaign photos |
| Brand Activation | Cover + Laundry photos + Airlines photos |
| Hertape Shopify | Cover + store screenshots |
| Maison Kolori | Cover + work photos |
| Operational Systems | Cover + Smart App photos + CWJ photos |
| Moneymani | Cover + app screenshots |
