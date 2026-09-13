"""
Automated Test Suite for E-Commerce Link Verification Engine
Smart Crossword Board Project (FAIL-010 / ADL-015)
"""

import pytest
from scripts.verify_ecommerce_links import (
    detect_platform,
    extract_asin,
    extract_bol_id,
    clean_html_title,
    parse_price,
    check_stock_status,
    extract_markdown_urls,
    verify_url,
    LinkCheckResult
)

def test_detect_platform():
    assert detect_platform("https://www.amazon.com.be/dp/B0GH7LXL2K") == "Amazon Belgium"
    assert detect_platform("https://www.amazon.fr/dp/B07RKG3C84") == "Amazon France"
    assert detect_platform("https://www.amazon.de/dp/B077CZ8YWH") == "Amazon Germany"
    assert detect_platform("https://www.bol.com/be/nl/p/product/9300000246441373/") == "Bol.com"
    assert detect_platform("https://shopnfc.com/en/nfc-stickers/115-nxp-ntag213-nfc-tags.html") == "ShopNFC"
    assert detect_platform("https://store.gototags.com/clear-wet-nfc-inlay-ntag213-22-mm-circle/") == "GoToTags"
    assert detect_platform("https://www.aliexpress.com/item/100500123456.html") == "AliExpress"
    assert detect_platform("https://example.com/item") == "Generic E-Commerce"

def test_extract_asin():
    assert extract_asin("https://www.amazon.com.be/dp/B0GH7LXL2K") == "B0GH7LXL2K"
    assert extract_asin("https://www.amazon.com.be/gp/product/B0GH7LXL2K") == "B0GH7LXL2K"
    assert extract_asin("https://www.amazon.fr/Product-Name/dp/B07RKG3C84?ref=xyz") == "B07RKG3C84"
    assert extract_asin("https://example.com/not-amazon") is None

def test_extract_bol_id():
    assert extract_bol_id("https://www.bol.com/be/nl/p/scrabble/9300000246441373/") == "9300000246441373"
    assert extract_bol_id("https://www.bol.com/nl/nl/p/product-title/9300000379963969/") == "9300000379963969"
    assert extract_bol_id("https://example.com/no-bol-id") is None

def test_clean_html_title():
    raw = "  <title>200 Pcs Lettres &amp; Chiffres &#x27;Scrabble&#x27; - &quot;Super&quot;</title>  "
    cleaned = clean_html_title(raw)
    assert cleaned == "200 Pcs Lettres & Chiffres 'Scrabble' - \"Super\""

def test_parse_price():
    # Amazon whole/fraction
    html_amazon = '<span class="a-price-whole">6<span class="a-price-decimal">,</span></span><span class="a-price-fraction">99</span>'
    assert parse_price(html_amazon) == 6.99

    # priceAmount JSON
    html_json = '{"sku":"123","priceAmount":22.80,"currency":"EUR"}'
    assert parse_price(html_json) == 22.80

    # Euro symbol prefix/suffix
    assert parse_price("<div>Prix: €8.99 TTC</div>") == 8.99
    assert parse_price("<div>Total: 14,50 €</div>") == 14.50

def test_check_stock_status():
    # Amazon in-stock
    amazon_in_stock = '<div id="availability"><span class="a-color-success">En stock</span></div><button id="add-to-cart-button">Add</button>'
    assert check_stock_status("Amazon Belgium", amazon_in_stock) is True

    # Amazon out-of-stock
    amazon_out_of_stock = '<div id="outOfStock">This item is currently unavailable</div>'
    assert check_stock_status("Amazon Belgium", amazon_out_of_stock) is False

    # Bol.com out-of-stock dialog
    bol_out = '<a href="?mode=openProductAvailabilityDialog">Stuur mij een bericht</a>'
    assert check_stock_status("Bol.com", bol_out) is False

    # ShopNFC in-stock
    shopnfc_in = '<span id="product-availability">In Stock</span>'
    assert check_stock_status("ShopNFC", shopnfc_in) is True

def test_extract_markdown_urls():
    md = """
    Check out [User Tile Product](https://www.amazon.com.be/dp/B0GH7LXL2K) and
    [Alternative Tiles](https://www.amazon.com.be/dp/B07RKG3C84).
    Also [Duplicate Link](https://www.amazon.com.be/dp/B0GH7LXL2K).
    """
    urls = extract_markdown_urls(md)
    assert len(urls) == 2
    assert "https://www.amazon.com.be/dp/B0GH7LXL2K" in urls
    assert "https://www.amazon.com.be/dp/B07RKG3C84" in urls

def test_live_user_product_verification():
    """Live integration test: verifies the user-provided Amazon Belgium product link."""
    res = verify_url("https://www.amazon.com.be/dp/B0GH7LXL2K", timeout=10)
    if not res.is_live and "Anti-bot" in (res.error_message or ""):
        pytest.skip("Amazon rate limit / bot challenge encountered")
    assert res.is_live is True
    assert res.status_code == 200
    assert res.is_in_stock is True
    assert res.price_eur in [5.99, 6.99]
    assert "200 Pcs Lettres en Bois" in (res.title or "")
    assert res.canonical_url is not None
    assert "B0GH7LXL2K" in res.canonical_url


def test_live_pn532_reader_verification():
    """Live integration test: verifies Hailege PN532 V4 module on Amazon Belgium."""
    res = verify_url("https://www.amazon.com.be/dp/B0CJY2GQZ8", timeout=10)
    if not res.is_live and "Anti-bot" in (res.error_message or ""):
        pytest.skip("Amazon rate limit / bot challenge encountered")
    assert res.is_live is True
    assert res.status_code == 200
    assert res.is_in_stock is True
    assert res.price_eur == 10.84
    assert "PN532" in (res.title or "")
    assert "B0CJY2GQZ8" in (res.canonical_url or "")

