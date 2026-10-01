# Vercel deployment notes

## Recommended setup
1. Import the repository into Vercel and set the project root to the repository root.
2. Keep the Next.js framework setting; `vercel.json` runs install and build commands from `frontend/`.
3. Keep the configured output directory `frontend/.next`.
4. Set `NEXT_PUBLIC_BACKEND_URL` to the public backend URL, with no trailing slash.
5. Add the `NEXT_PUBLIC_FIREBASE_*` values from `frontend/.env.example`.
6. Add the production frontend domain to Firebase Authentication's authorized domains.

## Required environment values
- `NEXT_PUBLIC_BACKEND_URL`
- Firebase public config values

Do not commit provider URLs or credentials to `vercel.json`; configure them in Vercel project environment settings.
