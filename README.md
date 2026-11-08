# peaklip-media

Promo videos for Peaklip's Instagram (@peaklipapp), served by GitHub Pages.

- `videos/` holds the approved videos for the coming week.
- `schedule.json` lists them with their caption and posting time. Only items with `"approved": true` are posted.
- The Peaklip server (Railway) checks the schedule every few minutes and publishes what's due through
  Instagram's official API. Status: https://clipfactory-production-e466.up.railway.app/social/status

Videos are removed a few days after they're posted.
