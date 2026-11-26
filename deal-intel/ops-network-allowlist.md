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
