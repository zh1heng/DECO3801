from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict, Optional


class SimpleNavigator:
    def __init__(self, headless: bool = True):
        import sys
        if sys.platform == "win32":
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="en-US"
        )
        self.page = self.context.new_page()

    def open_url(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass

        # 先等首屏基础元素
        for selector in ["body", "img", "a"]:
            try:
                self.page.wait_for_selector(selector, timeout=8000)
            except:
                pass

        # 核心：分段滚动，把下方内容触发出来
        self.smart_scroll_to_load_all()

        # 最后再补等一下
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        self.page.wait_for_timeout(2000)

    def smart_scroll_to_load_all(self, max_rounds: int = 30, step: int = 800):
        last_height = self.page.evaluate("document.body.scrollHeight")
        stable_rounds = 0

        for _ in range(max_rounds):
            current_y = 0
            new_content_loaded = False

            while current_y < last_height:
                self.page.evaluate(f"window.scrollTo(0, {current_y})")
                self.page.wait_for_timeout(1200)

                # 等图片尽量加载
                self.page.evaluate("""
                    () => {
                        const imgs = Array.from(document.images || []);
                        return Promise.all(
                            imgs.slice(0, 20).map(img => {
                                if (img.complete) return Promise.resolve();
                                return new Promise(resolve => {
                                    img.onload = img.onerror = resolve;
                                    setTimeout(resolve, 1500);
                                });
                            })
                        );
                    }
                """)

                current_y += step

                # 看页面高度有没有继续变大
                updated_height = self.page.evaluate("document.body.scrollHeight")
                if updated_height > last_height:
                    last_height = updated_height
                    new_content_loaded = True

            # 到底部后再等一会，给异步请求时间
            self.page.wait_for_timeout(2500)

            updated_height = self.page.evaluate("document.body.scrollHeight")

            if updated_height > last_height:
                last_height = updated_height
                new_content_loaded = True

            if new_content_loaded:
                stable_rounds = 0
            else:
                stable_rounds += 1

            # 连续两轮都没新内容，基本可以认为到底了
            if stable_rounds >= 2:
                break

        # 最后回到顶部再截图
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(1500)
    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def get_html(self) -> str:
        return self.page.content()

    def save_screenshot(self, path: str, full_page: bool = True) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=path, full_page=full_page)
        return path

    def extract_links(self) -> List[Dict[str, str]]:
        """
        提取当前页面的链接。
        返回格式:
        [
            {"text": "...", "href": "...", "absolute_url": "..."},
            ...
        ]
        """
        current_url = self.page.url
        raw_links = self.page.locator("a").evaluate_all(
            """
            elements => elements.map(a => ({
                text: (a.innerText || '').trim(),
                href: a.getAttribute('href') || ''
            }))
            """
        )

        cleaned_links = []
        for item in raw_links:
            href = item["href"].strip()
            text = item["text"].strip()

            if not href:
                continue
            if href.startswith("#"):
                continue
            if href.lower().startswith("javascript:"):
                continue
            if href.lower().startswith("mailto:"):
                continue
            if href.lower().startswith("tel:"):
                continue

            absolute_url = urljoin(current_url, href)

            cleaned_links.append({
                "text": text,
                "href": href,
                "absolute_url": absolute_url
            })

        return cleaned_links

    def choose_next_link(
        self,
        links: List[Dict[str, str]],
        same_domain_only: bool = True,
        keyword: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        从提取的链接里挑一个要跳转的目标链接。
        - same_domain_only=True: 只选同域名链接
        - keyword: 如果提供，优先选 text 或 url 中包含该关键词的链接
        """
        current_domain = urlparse(self.page.url).netloc

        filtered = []
        for link in links:
            target_domain = urlparse(link["absolute_url"]).netloc
            if same_domain_only and target_domain != current_domain:
                continue
            filtered.append(link)

        if not filtered:
            return None

        if keyword:
            keyword_lower = keyword.lower()
            for link in filtered:
                if keyword_lower in link["text"].lower() or keyword_lower in link["absolute_url"].lower():
                    return link

        # 默认选第一个同域且有效的链接
        return filtered[0]

    def go_to_link(self, link: Dict[str, str]) -> None:
        self.page.goto(link["absolute_url"], wait_until="domcontentloaded", timeout=60000)

        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass

        for selector in ["body", "img", "a"]:
            try:
                self.page.wait_for_selector(selector, timeout=8000)
            except:
                pass

        self.smart_scroll_to_load_all()

        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        self.page.wait_for_timeout(2000)
    def close(self) -> None:
        self.browser.close()
        self.playwright.stop()


def preview_links(links: List[Dict[str, str]], limit: int = 10) -> None:
    print("\n[提取到的链接预览]")
    if not links:
        print("  没有提取到可用链接")
        return

    for i, link in enumerate(links[:limit], start=1):
        text = link["text"] if link["text"] else "(无文本)"
        print(f"  {i}. text={text[:50]!r}")
        print(f"     href={link['href']}")
        print(f"     absolute_url={link['absolute_url']}")


if __name__ == "__main__":
    start_url = input("请输入起始网址: ").strip()
    keyword = input("请输入想优先跳转的关键词（可留空）: ").strip()

    navigator = SimpleNavigator(headless=True)

    try:
        print("\n=== 第一步：打开起始页 ===")
        navigator.open_url(start_url)
        print("当前标题:", navigator.get_title())
        print("当前URL:", navigator.get_current_url())

        start_html = navigator.get_html()
        print("起始页 HTML 长度:", len(start_html))

        start_screenshot = navigator.save_screenshot("outputs/start_page.png")
        print("起始页截图已保存:", start_screenshot)

        print("\n=== 第二步：提取当前页链接 ===")
        links = navigator.extract_links()
        print("提取到的可用链接数量:", len(links))
        preview_links(links, limit=10)

        print("\n=== 第三步：选择一个链接并跳转 ===")
        next_link = navigator.choose_next_link(
            links=links,
            same_domain_only=True,
            keyword=keyword if keyword else None
        )

        if not next_link:
            print("没有找到符合条件的下一页链接。")
        else:
            print("选中的链接:")
            print("  text =", next_link["text"] if next_link["text"] else "(无文本)")
            print("  url  =", next_link["absolute_url"])

            navigator.go_to_link(next_link)

            print("\n=== 第四步：跳转后页面信息 ===")
            print("新页面标题:", navigator.get_title())
            print("新页面URL:", navigator.get_current_url())

            next_html = navigator.get_html()
            print("新页面 HTML 长度:", len(next_html))

            next_screenshot = navigator.save_screenshot("outputs/next_page.png")
            print("新页面截图已保存:", next_screenshot)

            print("\n=== 第五步：输出 HTML 预览 ===")
            print(next_html[:1000])  # 只打印前1000个字符，避免太长

    except PlaywrightTimeoutError:
        print("[错误] 页面加载超时。")
    except Exception as e:
        print(f"[错误] 运行失败: {e}")
    finally:
        navigator.close()