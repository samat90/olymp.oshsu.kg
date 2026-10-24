"""End-to-end check of the contest tab watcher on the local stand (WSL):
    /opt/pw/bin/python scripts/dev/anticheat_check.py
Logs in as devstudent (taking part in "devtest"), leaves the contest tab for another site
four times and expects three warnings and then the disqualification; going to the Compiler
tab of our own site must not count."""
import sys

from playwright.sync_api import sync_playwright

SITE = 'http://127.0.0.1:8000'


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(SITE + '/accounts/login/?next=/contest/devtest/')
        page.fill('input[name=username]', 'devstudent')
        page.fill('input[name=password]', 'devstudent-local-2026')
        page.press('input[name=password]', 'Enter')
        page.wait_for_load_state('networkidle')
        page.goto(SITE + '/problem/000001')
        page.wait_for_load_state('networkidle')
        if not page.evaluate('!!window.OLYMP_ANTICHEAT'):
            print('FAIL: tracking is off on the contest page')
            return 1
        print('tracking on, warnings so far:', page.evaluate('window.OLYMP_ANTICHEAT.warnings'))

        # Headless Chromium keeps every tab "visible", so the switch is played the way a real
        # browser reports it: the page becomes hidden; for our own Compiler tab, that tab marks
        # itself active first (base.html does this on every page of the site).
        def leave(own_site_tab, expect_report):
            page.evaluate("""own => {
                if (own) localStorage.setItem('olymp-active-tab', JSON.stringify({id: 'other-tab', t: Date.now()}));
                Object.defineProperty(document, 'visibilityState', {value: 'hidden', configurable: true});
                document.dispatchEvent(new Event('visibilitychange'));
            }""", own_site_tab)
            page.wait_for_timeout(2500)
            page.evaluate("""() => {
                Object.defineProperty(document, 'visibilityState', {value: 'visible', configurable: true});
                document.dispatchEvent(new Event('visibilitychange'));
            }""")
            page.wait_for_timeout(500)
            modal = page.query_selector('.ac-modal')
            text = modal.inner_text().replace('\n', ' | ') if modal else ''
            print('%-22s modal: %s' % ('own Compiler tab' if own_site_tab else 'another site', text or '-'))
            if modal:
                page.click('.ac-btn')
                page.wait_for_load_state('networkidle')
            page.wait_for_timeout(4500)  # events closer than a few seconds count once
            return bool(modal) == expect_report

        ok = leave(True, expect_report=False)
        for _ in range(4):
            ok &= leave(False, expect_report=True)
        browser.close()
        print('OK' if ok else 'FAIL')
        return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
