from playwright.sync_api import sync_playwright
import time
import os

# ==================== 設定區 ====================
TOTAL_PAGES = 150        # 預計要下載的總頁數
SAVE_DIR = "hanlin_book" # 圖片儲存的資料夾名稱
WAIT_TIME = 4.5          # 翻頁後等待渲染的秒數 (稍微調高一點求穩定)
# ===============================================

def auto_download_book():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    with sync_playwright() as p:
        # 【升級 1】強制呼叫實體 Google Chrome，並隱藏自動化特徵
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",  # 關鍵：使用你電腦裡正版的 Chrome，解決引擎罷工問題
            args=["--disable-blink-features=AutomationControlled"] 
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        
        # 注入 JavaScript 抹除機器人指紋，騙過伺服器
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        page.goto("https://edisc3.hle.com.tw/edisc_v3/index.html")

        print("\n🛑 瀏覽器已啟動，程式目前暫停中。")
        print("1. 請手動登入平台。")
        print("2. 點擊開啟電子書（跳出新分頁也沒關係，程式會自動抓）。")
        print("3. 在電子書分頁翻到「要開始截圖的第一頁」，並確認畫面清晰。")
        
        input("\n👉 準備好後，請點擊終端機並按下 [Enter] 鍵...")

        print("\n🚀 開始自動翻頁截圖...")

        # 【升級 2】智慧抓取最新的分頁 (解決電子書開在新標籤頁的問題)
        all_pages = context.pages
        book_page = all_pages[-1]     # 鎖定陣列中的最後一個分頁 (即你的電子書)
        book_page.bring_to_front()    # 強制把該分頁拉到最上層顯示

        for i in range(1, TOTAL_PAGES + 1):
            page_str = f"{i:03d}"
            file_path = os.path.join(SAVE_DIR, f"page_{page_str}.png")
            
            try:
                # 針對新的 book_page 尋找畫布
                canvas = book_page.locator("canvas").first
                canvas.screenshot(path=file_path)
                print(f"✅ 已成功截圖並儲存：第 {page_str} 頁")
            except Exception as e:
                print(f"❌ 截圖失敗，可能找不到畫布：{e}")
                break

            # 針對新的 book_page 進行翻頁
            book_page.keyboard.press("ArrowRight")
            time.sleep(WAIT_TIME)

        print("\n🎉 全部下載任務完畢！請檢查資料夾。")
        browser.close()

if __name__ == "__main__":
    auto_download_book()