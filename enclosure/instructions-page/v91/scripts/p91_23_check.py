import asyncio
from playwright.async_api import async_playwright
OUT = "/home/claude/page/shots2/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []
        for name, vp, scheme in [("phone", {"width": 390, "height": 844}, "light"), ("wide", {"width": 1280, "height": 860}, "dark")]:
            ctx = await b.new_context(viewport=vp, color_scheme=scheme)
            pg = await ctx.new_page()
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto("http://localhost:8765/index.html")
            await pg.wait_for_selector(".head")
            for r in ["trial", "abs", "service"]:
                await pg.click(f'.seg button[data-r="{r}"]')
                await pg.click("#bList"); await pg.click("#lst a");
                n = 0
                while True:
                    n += 1
                    ov = await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                    h = await pg.evaluate("location.hash")
                    if ov > 1: errs.append(f"{name} {r} {h} overflow {ov}")
                    if name == "phone" and r != "abs" and h in ("#step-26", "#i-leads", "#i-print", "#step-10", "#i-after", "#i-plugs", "#sv-plate", "#i-tests", "#step-21", "#i-calib"):
                        await pg.screenshot(path=f"{OUT}{name}_{r}_{h[1:]}.png", full_page=True)
                    if name == "phone" and r == "abs" and h in ("#i-print", "#step-14", "#i-tests"):
                        await pg.screenshot(path=f"{OUT}{name}_{r}_{h[1:]}.png", full_page=True)
                    if name == "wide" and h in ("#step-14", "#i-calib", "#i-leads", "#step-19", "#step-05"):
                        await pg.screenshot(path=f"{OUT}{name}_{r}_{h[1:]}.png")
                    if await pg.is_disabled("#bNext"): break
                    await pg.click("#bNext")
                print(name, r, n, "pages")
            await pg.click('.seg button[data-r="trial"]')
            await pg.click("#bList"); await pg.click('#lst a[href="#step-14"]')
            await pg.fill('input[data-t="T9.l"]', "1.2")
            await pg.click('.seg button[data-r="abs"]')
            await pg.click("#bList"); await pg.click('#lst a[href="#step-14"]')
            await pg.fill('input[data-t="ABS T9.r"]', "1.25")
            await pg.click("#bRead")
            t = await pg.inner_text("#out"); print(t[:900])
            await pg.screenshot(path=f"{OUT}{name}_readings.png")
            await ctx.close()
        print("errors:", errs)
        await b.close()
asyncio.run(main())
