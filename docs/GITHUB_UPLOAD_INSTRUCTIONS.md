# GitHub upload instructions

## Static GitHub Pages demo

1. Create a new GitHub repository, for example `gi-spr-pcf-digital-twin`.
2. Upload the complete contents of this package to the repository root. Keep `index.html` at the root.
3. Go to **Settings → Pages**.
4. Select **Deploy from branch**.
5. Select branch `main` and folder `/root`.
6. Save and wait for GitHub Pages to build.

Your public link will look like:

```text
https://YOUR-USERNAME.github.io/gi-spr-pcf-digital-twin/
```

## Important

GitHub Pages runs only the static frontend. The backend folder is included for local, Render, Replit, Railway, or Docker deployment, but it will not run on GitHub Pages.
