import os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
root = Path(__file__).parent
signer = root / 'test-signer.mjs'
def call(value=None):
    args = ['node',str(signer)] + (['pubkey'] if value is None else [])
    return subprocess.check_output(args,input=value,text=True).strip()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_EXECUTABLE') or None,args=['--no-sandbox'])
    page=browser.new_page()
    failures=[]
    page.on('pageerror', lambda err: failures.append(str(err)))
    page.expose_function('devnetTestKey',call)
    page.add_init_script('''window.phantom={solana:{publicKey:null,async connect(){const address=await window.devnetTestKey(null);this.publicKey={toString:()=>address};},async signTransaction(tx){const b64=btoa(String.fromCharCode(...tx.serialize()));const raw=await window.devnetTestKey(b64);return tx.constructor.deserialize(Uint8Array.from(atob(raw),c=>c.charCodeAt(0)));}}};''')
    page.goto(os.getenv('DEMO_URL','http://127.0.0.1:18843/'))
    expect(page.locator('#balances')).to_contain_text('В хранилище:',timeout=15000)
    expect(page.locator('#admin')).to_be_hidden()
    page.locator('[data-action=deposit]').click()
    expect(page.locator('#status')).to_have_text('Сначала подключите кошелёк')
    page.locator('#connect').click()
    expect(page.locator('#admin')).to_be_visible(timeout=15000)
    def act(name):
        b=page.locator(f'[data-action={name}]'); b.click(); expect(b).to_be_enabled(timeout=90000)
        status=page.locator('#status'); print(name,status.inner_text(),flush=True); expect(status).to_contain_text('подтвержден',ignore_case=True); print(status.locator('a').get_attribute('href'),flush=True)
    def convert_all():
        import re
        match=re.search(r', ([\d.]+) B\.',page.locator('#balances').inner_text())
        assert match, 'Quote balance not shown'
        quote=match.group(1)
        if quote!='0.000000':
            page.locator('#direction').select_option('ba');page.locator('#swapAmount').fill(quote);act('swap')
    page.locator('#amount').fill('1');
    if 'открыта' in page.locator('#state').inner_text():
        page.locator('[data-action=withdraw]').click();expect(page.locator('#status')).to_contain_text('Сначала администратор'); act('close')
    convert_all()
    page.locator('#amount').fill('0');page.locator('[data-action=deposit]').click();expect(page.locator('#status')).to_contain_text('Сумма вне диапазона')
    page.locator('#amount').fill('1');act('deposit');
    page.locator('#direction').select_option('ab');page.locator('#swapAmount').fill('5');act('swap');
    page.locator('#liquidity').fill('50000000');act('open');act('fees');act('close');convert_all();
    page.locator('#amount').fill('0.5');act('withdraw');
    assert not failures, failures
    print('Browser Devnet round trip PASS')
