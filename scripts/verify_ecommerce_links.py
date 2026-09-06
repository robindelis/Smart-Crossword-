#!/usr/bin/env python3
"""
E-Commerce Link Verification & Price Extraction Engine
Smart Crossword Board Project (FAIL-010 / ADL-015)

Audits URLs on Amazon (.com.be, .fr, .de), Bol.com, ShopNFC, GoToTags, and generic sites.
Enforces that every cited link is active (HTTP 200), extracts canonical product URLs,
titles, prices in EUR, and in-stock status using modern browser headers.
"""

import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-BE,nl-BE,en-US,en;q=0.9,fr;q=0.8,nl;q=0.8,de;q=0.7",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

@dataclass
class LinkCheckResult:
    url: str
    platform: str
    status_code: int
    is_live: bool
    is_in_stock: bool
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    price_eur: Optional[float] = None
    product_id: Optional[str] = None
    error_message: Optional[str] = None

def detect_platform(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if "amazon.com.be" in hostname:
        return "Amazon Belgium"
    elif "amazon.fr" in hostname:
        return "Amazon France"
    elif "amazon.de" in hostname:
        return "Amazon Germany"
    elif "amazon." in hostname:
        return f"Amazon ({hostname})"
    elif "bol.com" in hostname:
        return "Bol.com"
    elif "shopnfc.com" in hostname:
        return "ShopNFC"
    elif "gototags.com" in hostname:
        return "GoToTags"
    elif "aliexpress.com" in hostname:
        return "AliExpress"
    return "Generic E-Commerce"

def extract_asin(url: str) -> Optional[str]:
    match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
    return match.group(1) if match else None

def extract_bol_id(url: str) -> Optional[str]:
    match = re.search(r'/(?:p/[^/]+/|p/)([0-9]{16})', url)
    return match.group(1) if match else None

def clean_html_title(raw_title: str) -> str:
    cleaned = re.sub(r'<[^>]*>', '', raw_title)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.replace('&amp;', '&').replace('&#x27;', "'").replace('&quot;', '"')
    return cleaned

def parse_price(html_content: str) -> Optional[float]:
    # 1. Amazon price patterns: whole and fraction
    whole_match = re.search(r'a-price-whole">([0-9]+)', html_content)
    fraction_match = re.search(r'a-price-fraction">([0-9]{2})', html_content)
    if whole_match:
        whole = whole_match.group(1)
        fraction = fraction_match.group(1) if fraction_match else "00"
        try:
            return float(f"{whole}.{fraction}")
        except ValueError:
            pass

    # 2. priceAmount JSON
    price_json = re.search(r'"priceAmount":([0-9.]+)', html_content)
    if price_json:
        try:
            return float(price_json.group(1))
        except ValueError:
            pass

    # 3. Currency symbol pattern: €XX.XX or XX,XX €
    eur_match = re.search(r'(?:€\s*|EUR\s*)([0-9]+[.,][0-9]{2})', html_content)
    if eur_match:
        val_str = eur_match.group(1).replace(',', '.')
        try:
            return float(val_str)
        except ValueError:
            pass

    eur_match_suffix = re.search(r'([0-9]+[.,][0-9]{2})\s*(?:€|EUR)', html_content)
    if eur_match_suffix:
        val_str = eur_match_suffix.group(1).replace(',', '.')
        try:
            return float(val_str)
        except ValueError:
            pass

    return None

def check_stock_status(platform: str, html: str) -> bool:
    if "amazon" in platform.lower():
        # Check explicit out-of-stock indicators
        if 'id="outOfStock"' in html:
            return False
        
        # Check availability container
        avail_match = re.search(r'<div[^>]*id=["\']availability["\'][^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
        if avail_match:
            avail_text = avail_match.group(1).lower()
            if any(term in avail_text for term in ["actuellement indisponible", "currently unavailable", "derzeit nicht verfügbar"]):
                return False
            if any(term in avail_text for term in ["en stock", "in stock", "auf lager", "stock"]):
                return True

        # Check for presence of cart buttons
        if "add-to-cart-button" in html or "buy-now-button" in html:
            return True

        # Check if price is present (unpriced items are usually unavailable)
        price = parse_price(html)
        return price is not None

    elif "bol.com" in platform.lower():
        if "openProductAvailabilityDialog" in html or "Niet leverbaar" in html:
            return False
        if "In winkelwagen" in html or "schema.org/InStock" in html:
            return True
        return True

    elif "shopnfc" in platform.lower():
        if "In Stock" in html or "product-available" in html:
            return True
        if "Out of stock" in html:
            return False
        return True

    # Generic: assume in stock if HTTP 200 and not explicitly 404/unavailable
    return True

def verify_url(url: str, timeout: int = 10) -> LinkCheckResult:
    platform = detect_platform(url)
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            content_bytes = response.read()
            html = content_bytes.decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return LinkCheckResult(
            url=url,
            platform=platform,
            status_code=e.code,
            is_live=False,
            is_in_stock=False,
            error_message=f"HTTP error: {e.code} {e.reason}"
        )
    except Exception as e:
        return LinkCheckResult(
            url=url,
            platform=platform,
            status_code=0,
            is_live=False,
            is_in_stock=False,
            error_message=f"Connection error: {str(e)}"
        )

    # Detect 404 / Missing page indicators in HTML
    missing_indicators = [
        "Page Not Found",
        "Looking for something?",
        "Désolé, nous ne pouvons pas trouver cette page",
        "Tut uns leid",
        "404 Not Found",
        "Niet gevonden",
        "Product niet gevonden"
    ]
    is_missing = any(ind.lower() in html.lower() for ind in missing_indicators if "<title>" in html[:1000])

    # Extract Canonical URL
    canonical_match = re.search(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if not canonical_match:
        canonical_match = re.search(r'<link\s+[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', html, re.IGNORECASE)
    canonical_url = canonical_match.group(1) if canonical_match else url

    # Extract Title
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = clean_html_title(title_match.group(1)) if title_match else None

    # Check for Captcha / Bot Challenge
    is_bot_challenge = (
        (title and any(bot in title.lower() for bot in ["server busy", "robot check", "captcha"]))
        or "validateCaptcha" in html
        or ("a-no-js" in html[:300] and len(html) < 5000)
    )
    if is_bot_challenge:
        # Fallback to curl with modern HTTP/2 and TLS fingerprint
        try:
            import subprocess
            curl_cmd = [
                "curl", "-sL", "--max-time", str(timeout),
                "-A", DEFAULT_HEADERS["User-Agent"],
                "-H", f"Accept-Language: {DEFAULT_HEADERS['Accept-Language']}",
                "-H", "Sec-Ch-Ua: \"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"128\", \"Google Chrome\";v=\"128\"",
                "-H", "Sec-Ch-Ua-Mobile: ?0",
                "-H", "Sec-Ch-Ua-Platform: \"Windows\"",
                url
            ]
            res = subprocess.run(curl_cmd, capture_output=True, text=True, errors='replace')
            if res.returncode == 0 and len(res.stdout) > 5000:
                curl_html = res.stdout
                c_title_m = re.search(r'<title>(.*?)</title>', curl_html, re.IGNORECASE | re.DOTALL)
                c_title = clean_html_title(c_title_m.group(1)) if c_title_m else None
                c_is_bot = (
                    (c_title and any(bot in c_title.lower() for bot in ["server busy", "robot check", "captcha"]))
                    or "validateCaptcha" in curl_html
                    or ("a-no-js" in curl_html[:300] and len(curl_html) < 5000)
                )
                if not c_is_bot:
                    html = curl_html
                    title = c_title
                    is_bot_challenge = False
                    status_code = 200
        except Exception:
            pass

    if is_bot_challenge:
        return LinkCheckResult(
            url=url,
            platform=platform,
            status_code=status_code,
            is_live=False,
            is_in_stock=False,
            canonical_url=canonical_url,
            title=title,
            error_message="Anti-bot challenge or captcha triggered"
        )

    if is_missing or (title and "404" in title):
        return LinkCheckResult(
            url=url,
            platform=platform,
            status_code=404,
            is_live=False,
            is_in_stock=False,
            canonical_url=canonical_url,
            title=title,
            error_message="Product page not found (404)"
        )

    # Determine Stock Status
    is_in_stock = check_stock_status(platform, html)

    # Extract Price
    price_eur = parse_price(html)

    # Extract Product ID
    asin = extract_asin(url) or extract_asin(canonical_url)
    bol_id = extract_bol_id(url) or extract_bol_id(canonical_url)
    product_id = asin or bol_id

    return LinkCheckResult(
        url=url,
        platform=platform,
        status_code=status_code,
        is_live=True,
        is_in_stock=is_in_stock,
        canonical_url=canonical_url,
        title=title,
        price_eur=price_eur,
        product_id=product_id
    )

def extract_markdown_urls(content: str) -> List[str]:
    # Match markdown links: [text](https://...)
    urls = re.findall(r'\[(?:[^\]]*)\]\((https?://[^)]+)\)', content)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u in urls:
        clean_u = u.strip()
        if clean_u not in seen:
            seen.add(clean_u)
            deduped.append(clean_u)
    return deduped

def scan_markdown_file(filepath: str, timeout: int = 10) -> List[LinkCheckResult]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    urls = extract_markdown_urls(content)
    results = []
    for u in urls:
        # Only check e-commerce domains, skip repo internal links
        if any(dom in u for dom in ["amazon.", "bol.com", "shopnfc.com", "gototags.com", "aliexpress.com"]):
            res = verify_url(u, timeout=timeout)
            results.append(res)
    return results

def main():
    parser = argparse.ArgumentParser(description="Verify e-commerce links and extract live product metadata.")
    parser.add_argument("--check-url", type=str, help="Single URL to verify")
    parser.add_argument("--check-asin", type=str, help="ASIN to check on specified platform")
    parser.add_argument("--platform", type=str, default="amazon.com.be", help="Amazon marketplace domain (default: amazon.com.be)")
    parser.add_argument("--scan-file", type=str, help="Markdown file to scan and verify all contained e-commerce links")
    parser.add_argument("--export-json", type=str, help="Path to export verification results as JSON")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds")

    args = parser.parse_args()

    results: List[LinkCheckResult] = []

    if args.check_url:
        print(f"Checking URL: {args.check_url} ...")
        res = verify_url(args.check_url, timeout=args.timeout)
        results.append(res)
    elif args.check_asin:
        url = f"https://www.{args.platform}/dp/{args.check_asin}"
        print(f"Checking ASIN {args.check_asin} on {args.platform} ({url}) ...")
        res = verify_url(url, timeout=args.timeout)
        results.append(res)
    elif args.scan_file:
        print(f"Scanning markdown file: {args.scan_file} ...")
        results = scan_markdown_file(args.scan_file, timeout=args.timeout)
    else:
        parser.print_help()
        sys.exit(1)

    print("\n" + "=" * 95)
    print(f"{'Platform':<16} | {'Status':<8} | {'Stock':<6} | {'Price':<8} | {'Title / Canonical URL'}")
    print("-" * 95)
    
    all_passed = True
    for r in results:
        status_str = f"HTTP {r.status_code}" if r.is_live else "DEAD"
        stock_str = "IN" if r.is_in_stock else "OUT"
        price_str = f"€{r.price_eur:.2f}" if r.price_eur is not None else "N/A"
        title_snippet = (r.title[:48] + "...") if r.title and len(r.title) > 50 else (r.title or r.url)
        
        print(f"{r.platform:<16} | {status_str:<8} | {stock_str:<6} | {price_str:<8} | {title_snippet}")
        if not r.is_live or not r.is_in_stock:
            all_passed = False
            if r.error_message:
                print(f"  └── [FAILURE]: {r.error_message}")
        if r.canonical_url:
            print(f"  └── Canonical: {r.canonical_url}")

    print("=" * 95)

    if args.export_json:
        with open(args.export_json, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        print(f"Results exported to: {args.export_json}")

    if not all_passed:
        print("\nWARNING: One or more links failed live validation.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All inspected links are 100% live and in stock.")
        sys.exit(0)

if __name__ == "__main__":
    main()
