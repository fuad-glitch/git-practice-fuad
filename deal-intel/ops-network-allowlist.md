# Proposed network allowlist: Default cloud environment

Purpose: let the hourly task read sellers' own product and offer pages (V3 verification).
The task only reads pages. It never logs in, buys or submits forms.
Exact hostnames only; wildcards are not accepted. Apex and www are both listed where a site redirects between them.

## A. AI providers (25)
openai.com, chatgpt.com, www.anthropic.com, claude.com, one.google.com, gemini.google.com, www.perplexity.ai,
cursor.com, github.com, www.midjourney.com, runwayml.com, elevenlabs.io, x.ai, mistral.ai, openrouter.ai,
www.together.ai, groq.com, replicate.com, windsurf.com, www.jetbrains.com, n8n.io, www.make.com, zapier.com,
www.adobe.com, appsumo.com

## B. Hosting and cloud (27)
www.hetzner.com, www.digitalocean.com, www.vultr.com, contabo.com, www.ovhcloud.com, eco.ovhcloud.com,
www.hostinger.com, www.cloudways.com, www.cloudflare.com, www.namecheap.com, porkbun.com, www.linode.com,
www.runpod.io, lambda.ai, vast.ai, cloud.vast.ai, vercel.com, fly.io, railway.com, render.com, supabase.com, neon.com,
www.backblaze.com, wasabi.com, lowendtalk.com, lowendbox.com, www.akamai.com

## C/D. London iPhone and laptop sellers (18)
www.apple.com, www.johnlewis.com, www.currys.co.uk, www.argos.co.uk, www.amazon.co.uk, www.very.co.uk,
www.selfridges.com, www.backmarket.co.uk, www.giffgaff.com, www.musicmagpie.co.uk, uk.webuy.com, www.scan.co.uk,
www.box.co.uk, www.laptopsdirect.co.uk, www.lenovo.com, www.dell.com, www.hp.com, www.asus.com

Total: 70 hosts.

Known limitation: Amazon UK, Currys and John Lewis use bot protection. They may still refuse automated reads after
being allowed. Deals that can only be confirmed there may stay UNVERIFIED.

## Applied 26 Nov 2026: 34 essential hosts only (two approval cards)
Network access stays Limited, package managers stay allowed, no wildcards. The 36 optional hosts were not added.

### Access test, 26 Nov ~14:00 UTC
- **Product page readable with prices (11):** elevenlabs.io/pricing, apple.com/uk (iPhone and MacBook Pro shop),
  backmarket.co.uk/en-gb, scan.co.uk laptops, hostinger.com Black Friday page, ovhcloud.com/en-gb/black-friday,
  digitalocean.com/pricing, runpod.io/pricing, lenovo.com/gb/en, cursor.com/pricing, claude.com/pricing.
- **Home page loads (200; product pages not yet tested):** gemini.google.com, openai.com, chatgpt.com, anthropic.com,
  perplexity.ai, hetzner.com, cloudflare.com, vast.ai.
- **Proxy allows these, but the site blocks automated requests:** adobe.com, argos.co.uk and dell.com (Akamai
  "Access Denied"); currys.co.uk, contabo.com, vultr.com and namecheap.com (Cloudflare); johnlewis.com (connection reset);
  amazon.co.uk (empty 202). Deals at these sellers stay UNVERIFIED unless another primary page can be read.
- **Redirect to a host not on the list (proxy blocks the destination):** runwayml.com -> runway.com,
  lambda.ai -> lambda.com, www.box.co.uk -> box.co.uk. ovhcloud.com works via its /en-gb/ paths.
