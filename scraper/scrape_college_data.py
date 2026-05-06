"""
Web Scraper Module for BVRIT College Website
Full BFS crawler — discovers and scrapes ALL internal pages automatically.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
from urllib.parse import urljoin, urlparse
from collections import deque

# Target college website
BASE_URL = "https://bvrit.ac.in"

# Seed URLs — actual pages discovered from bvrit.ac.in (March 2026)
SEED_URLS = [
    # ── Core / About ──────────────────────────────────────────────
    "/",
    "/about-bvrit/",
    "/about-campus/",
    "/about-society-sves/",
    "/vision-mission-and-quality-policy/",
    "/contact-us/",
    "/mandatory-disclosure/",
    "/leadership-team/",
    "/education-trustees/",
    "/governing-body/",
    "/finance-committee/",
    "/academic-council/",
    "/board-of-studies-bos/",
    "/central-committees/",
    "/structure-and-functions/",
    "/service-rules/",
    "/statutory-declaration/",
    "/about-r-d/",
    "/careers/",
    "/photo-gallery/",
    "/latest-news/",
    "/notifications/",
    "/award/",
    "/news-in-media/",
    "/bvrit-going-green/",

    # ── Admissions ────────────────────────────────────────────────
    "/admission-process/",
    "/page_category/admissions/",
    "/student-information-e-cap/",
    "/scholarships/",
    "/instructions-to-the-students/",

    # ── Academics / Programs ──────────────────────────────────────
    "/departments/",
    "/under-graduate/",
    "/post-graduate-pg/",
    "/academic-regulations/",
    "/academic-calendars/",
    "/time-tables/",
    "/downloads/",
    "/e-content/",

    # ── CSE ───────────────────────────────────────────────────────
    "/cse/",
    "/cse/about-hod/",
    "/cse/faculty/",
    "/cse/curriculum/",
    "/cse/laboratories/",
    "/cse/department-placements/",
    "/cse/awards-recognition/",
    "/cse/publications/",
    "/cse/funding-projects/",
    "/cse/centers-of-excellence/",
    "/cse/e-resources/",
    "/cse/cse-vedic-activities/",
    "/cse/academic-activities-during-lockdown/",
    "/cse-pg/",

    # ── CSE - AI & ML ─────────────────────────────────────────────
    "/cse-ai-ml/",
    "/cse-ai-ml/program-coordinator/",
    "/cse-ai-ml/faculty/",
    "/cse-ai-ml/curriculum/",
    "/cse-ai-ml/academic-laboratories/",
    "/cse-ai-ml/vision-mission-peos-pos-and-psos/",
    "/cse-ai-ml/placement-readiness/",
    "/cse-ai-ml/research-and-development/",
    "/cse-ai-ml/elearning/",
    "/cse-ai-ml/industry-and-academic-collaborations/",
    "/cse-ai-ml/memorandum-of-understanding/",

    # ── CSE - Data Science ────────────────────────────────────────
    "/cse-ds/",
    "/cse-ds/about-hod/",
    "/cse-ds/program-coordinator/",
    "/cse-ds/faculty/",
    "/cse-ds/curriculum/",
    "/cse-ds/special-labs-academic-laboratories-infrastructure/",
    "/cse-ds/vision-mission-pos-psos-peos/",
    "/cse-ds/placement-readiness-trainings/",
    "/cse-ds/research-and-development/",
    "/cse-ds/elearning/",
    "/cse-ds/industry-academic-collaboration-collaborations/",

    # ── CSBS ──────────────────────────────────────────────────────
    "/csbs/",
    "/csbs/about-hod/",
    "/csbs/program-coordinator-csbs/",
    "/csbs/faculty/",
    "/csbs/curriculum/",
    "/csbs/infrastructure/",
    "/csbs/events/",
    "/csbs/e-learnings/",
    "/csbs/mous/",
    "/csbs/interns-placements/",
    "/csbs/students-achievements/",
    "/csbs/faculty-achievements/",
    "/csbs/research-development/",
    "/csbs/projects/",

    # ── AI & DS ───────────────────────────────────────────────────
    "/aids/",
    "/aids/about-hod/",
    "/aids/faculty/",
    "/aids/curriculum/",
    "/aids/special-labs-academic-laboratories-infrastructure/",
    "/aids/vision-mission-pos-psos-peos/",
    "/aids/placement-readiness-training/",
    "/aids/research-and-development/",
    "/aids/elearning/",
    "/aids/mous/",

    # ── IT ────────────────────────────────────────────────────────
    "/it/",
    "/it/about-hod/",
    "/it/teaching-faculty-it/",
    "/it/curriculum/",
    "/it/special-labs/",
    "/it/center-of-excellence/",
    "/it/department-placements/",
    "/it/awards-recognition/",
    "/it/publications/",
    "/it/funding-projects/",
    "/it/industry-institute-interaction/",
    "/it/research-consultancy/",
    "/it/student-achievements/",
    "/it/innovative-teaching-methods/",
    "/it/roll-of-honour/",
    "/it/news-letters-magazines/",
    "/it/vedic-activities/",
    "/it/academic-activities-during-lockdown/",

    # ── ECE ───────────────────────────────────────────────────────
    "/ece/",
    "/ece/about-hod/",
    "/ece/faculty/",
    "/ece/curriculum/",
    "/ece/laboratories/",
    "/ece/special-labs/",
    "/ece/department-placements/",
    "/ece/awards-recognition/",
    "/ece/ece-publications/",
    "/ece/research-and-funded-projects/",
    "/ece/consultancy-projects/",
    "/ece/student-academic-projects/",
    "/ece/workshops/",
    "/ece/ieee-student-branch-chapter/",
    "/ece/tlp/",
    "/ece/vedic-activities/",
    "/ece/latest-results/",
    "/ece/academic-activities-during-lockdown/",

    # ── EEE ───────────────────────────────────────────────────────
    "/eee/",
    "/eee/about-hod/",
    "/eee/faculty/",
    "/eee/curriculum/",
    "/eee/laboratories/",
    "/eee/department-placements/",
    "/eee/news-events-awards-recognition/",
    "/eee/publications/",
    "/eee/funding-projects/",
    "/eee/special-projects/",
    "/eee/consultancy/",
    "/eee/teaching-learning-practices/",
    "/eee/department-magazine-news-letter/",
    "/eee/latest-results/",
    "/eee/academic-activities-during-lockdown/",

    # ── Mechanical ────────────────────────────────────────────────
    "/mech/",
    "/mech/about-hod/",
    "/mech/faculty/",
    "/mech/curriculum/",
    "/mech/laboratories/",
    "/mech/department-placements/",
    "/mech/awards-recognition/",
    "/mech/publications/",
    "/mech/funding-projects/",
    "/mech/internships/",
    "/mech/gate-coaching-sessions/",
    "/mech/alumni-connect/",
    "/mech/altairs-center-of-excellence/",
    "/mech/teaching-learning-practices/",
    "/mech/vedic-activities/",
    "/mech/student-list/",
    "/mech/latest-results/",
    "/mech/academic-activities-during-lockdown/",

    # ── Civil ─────────────────────────────────────────────────────
    "/civil/",
    "/civil/about-hod/",
    "/civil/faculty/",
    "/civil/curriculum/",
    "/civil/laboratories/",
    "/civil/department-placements/",
    "/civil/awards-recognition/",
    "/civil/publications/",
    "/civil/funding-projects/",
    "/civil/events-organized/",
    "/civil/student-activities/",
    "/civil/industry-interactions/",
    "/civil/iirs-outreach-programme/",
    "/civil/civil-vedic-activities/",
    "/civil/vnccc_bvritn/",

    # ── Chemical ──────────────────────────────────────────────────
    "/che/",
    "/che/about-hod/",
    "/che/faculty/",
    "/che/curriculum/",
    "/che/laboratories/",
    "/che/department-placements/",
    "/che/awards-recognition/",
    "/che/publications/",
    "/che/rd-and-funding-projects/",
    "/che/events/",
    "/che/student-academic-projects/",
    "/che/iiche-bvrit-chapter/",
    "/che/innovative-teaching-and-learning-practices/",
    "/che/news-letter-chemtrendz/",
    "/che/process-intensification-and-research-lab/",
    "/che/the-cosmos/",

    # ── BME ───────────────────────────────────────────────────────
    "/bme/",
    "/bme/about-hod/",
    "/bme/faculty/",
    "/bme/curriculum/",
    "/bme/laboratories/",
    "/bme/placements-and-higher-studies/",
    "/bme/publications/",
    "/bme/department-events/",
    "/bme/student-academic-projects/",
    "/bme/guest-lectures-and-student-achievements/",
    "/bme/teaching-learning-practices/",
    "/bme/bme-alumni/",
    "/bme/bme-vedic-activities/",
    "/bme/student-list/",
    "/bme/latest-results/",
    "/bme/admission-enquiry/",
    "/bme/academic-activities-during-lockdown/",
    "/bme/mous/",

    # ── Pharmaceutical ────────────────────────────────────────────
    "/phe/",
    "/phe/about-hod/",
    "/phe/faculty/",
    "/phe/curriculum/",
    "/phe/laboratories/",
    "/phe/department-placements/",
    "/phe/awards-recognitions/",
    "/phe/publications/",
    "/phe/funding-projects/",
    "/phe/department-activities/",
    "/phe/student-academic-projects/",
    "/phe/student-activities-and-achievements/",
    "/phe/teaching-learning-practices/",
    "/phe/department-magazine/",
    "/phe/coe/",
    "/phe/phe-vedic-activities/",
    "/phe/news-in-media/",
    "/phe/student-list/",
    "/phe/latest-results/",
    "/phe/academic-activities-during-lockdown/",

    # ── BS&H / Freshman ───────────────────────────────────────────
    "/bs-h/",
    "/bs-h/about-hod/",
    "/bs-h/faculty/",
    "/bs-h/curriculum/",
    "/bs-h/laboratories/",
    "/bs-h/awards-recognition/",
    "/bs-h/departmental-activities/",
    "/bs-h/funding-projects/",
    "/bs-h/academic-activities-during-lockdown/",

    # ── MBA ───────────────────────────────────────────────────────
    "/mba/",
    "/mba/about-hod/",
    "/mba/faculty/",
    "/mba/curriculum/",
    "/mba/department-placements/",
    "/mba/publications/",

    # ── PG Programs ───────────────────────────────────────────────
    "/data-sciences-ds-pg/",
    "/es-ece-pg/",
    "/eps/",
    "/evt-pg/",
    "/vlsi-ece-pg/",
    "/engineering-design-mech-pg/",

    # ── Placements ────────────────────────────────────────────────
    "/placement-statistics/",
    "/placements-team/",
    "/about-placement-cell/",
    "/recruiters-partnerships/",
    "/career-guidance/",
    "/internship-opportunities/",
    "/skill-development/",

    # ── Examinations ──────────────────────────────────────────────
    "/examination-branch-contacts/",
    "/results/",
    "/valuation-procedure/",
    "/malpractice-rules/",

    # ── Research ──────────────────────────────────────────────────
    "/research-centers-special-labs/",
    "/research-papers-published/",
    "/research-grant-projects/",
    "/research-committee/",
    "/research-advisory-committee/",
    "/thrust-areas-of-rd/",
    "/patents/",

    # ── Campus Life ───────────────────────────────────────────────
    "/hostels/",
    "/transport/",
    "/library/",
    "/location/",
    "/sports-and-fitness/",
    "/students-life/",
    "/big-byte-food-court/",
    "/boat-club/",
    "/wellness-centre/",
    "/centennial-health-centre/",
    "/e-classroom/",
    "/vishnu-audio-visual-centre/",
    "/bvrit-knowledge-centre/",
    "/literary-delight/",
    "/toastmasters/",
    "/club-inquizitive/",
    "/alumni/",
    "/alumni-spotlight/",

    # ── Special Labs / Centers ────────────────────────────────────
    "/cloud-computing-center/",
    "/aicte-idea-lab/",
    "/national-instruments-lab/",
    "/texas-instruments-lab/",
    "/center-for-automotive-technologies/",
    "/center-for-automotive-electronics-cae/",
    "/center-for-embedded-systems-and-iot/",
    "/center-for-nanotechnology/",
    "/center-for-vlsi-design/",
    "/center-of-excellence-in-artificial-intelligence-machine-learning/",
    "/centre-for-advanced-communications-lab/",
    "/centre-for-cognitive-sciences/",
    "/computational-fluid-dynamics-cfd/",
    "/emerging-technology-center/",
    "/ham-lab/",
    "/robotics-center-for-enhanced-learning/",
    "/vlsi-automation-centre/",
    "/vishnu-space-engineering-center-2/",
    "/tvs-haritha-techserve/",
    "/assistive-technology-lab-atl/",
    "/isro-start-outreach-program/",
    "/441-kwp-solar-pv-plant/",
    "/indnor-solar-rd-project/",

    # ── Accreditation / Governance ────────────────────────────────
    "/naac/",
    "/nirf/",
    "/nba-documents-2k24/",
    "/aicte-affiliation-reports/",
    "/aishe-reports/",
    "/ariia-reports/",
    "/internal-quality-assurance-cell/",
    "/internal-quality-assurance-cell/external-academic-and-administrative-audit-reports/",
    "/institute-development-plan/",
    "/ugc-compliance/",
    "/ugc-accessibility-guidelines-and-standards/",
    "/university-ombudsperson/",

    # ── Entrepreneurship / Social ─────────────────────────────────
    "/entrepreneurship-development-cell-edc/",
    "/msme-business-incubator/",
    "/institution-innovation-council-iic/",
    "/innovation-and-entrepreneurship-i-e-policy/",
    "/national-innovation-and-startup-policy-nisp/",
    "/rural-women-technology-park/",
    "/unnat-bharat-abhiyan/",
    "/institutional-ethics-committee/",
    "/women-faculty-in-administrative-positions/",
    "/graduate-study-abroad-center-gsac/",
]

# URL patterns to SKIP (non-content pages)
SKIP_PATTERNS = [
    r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|jpg|jpeg|png|gif|svg|mp4|mp3|css|js)(\?|$)',
    r'/wp-admin/',
    r'/wp-login',
    r'/feed/',
    r'/tag/',
    r'/author/',
    r'\?s=',       # search queries
    r'\?page_id=', # WP page IDs (prefer slug URLs)
    r'#',          # anchors
    r'mailto:',
    r'tel:',
    r'javascript:',
]

# Output paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "scraped_college_content.txt")
OUTPUT_JSON = os.path.join(DATA_DIR, "scraped_pages.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Crawl limits
MAX_PAGES = 800        # stop after this many successful pages
CRAWL_DELAY = 0.8      # seconds between requests (be polite)
MIN_CONTENT_LEN = 100  # skip pages with less content than this


def should_skip_url(url):
    """Return True if the URL should be skipped."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, url, re.I):
            return True
    return False


def is_internal(url):
    """Return True if the URL belongs to the target domain."""
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc.replace("www.", "") == urlparse(BASE_URL).netloc.replace("www.", "")


def normalize_url(url):
    """Normalize URL — strip fragments, trailing slashes variation, query strings."""
    parsed = urlparse(url)
    # Rebuild without fragment; keep query only if meaningful
    path = parsed.path
    if path and not path.endswith('/'):
        path = path + '/'
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    return normalized.lower()


def clean_text(text):
    """Clean extracted text."""
    text = re.sub(r'\s+', ' ', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.strip()


def extract_links(soup, current_url):
    """Extract all internal links from a page."""
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        # Resolve relative URLs
        full_url = urljoin(current_url, href)
        # Only keep internal links
        if is_internal(full_url):
            links.add(full_url)
    return links


def extract_page_content(url):
    """Fetch a page and extract its meaningful text content."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        # Only process HTML pages
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return None, set()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Collect internal links BEFORE removing nav/footer
        links = extract_links(soup, url)

        # Remove non-content elements
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'footer', 'header']):
            tag.decompose()

        # Get title
        title_tag = soup.find('title')
        title_text = clean_text(title_tag.get_text()) if title_tag else ""

        # Find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'\b(content|main|entry|page-content|post-content|site-content)\b', re.I)) or
            soup.find('div', id=re.compile(r'\b(content|main|entry|page-content)\b', re.I)) or
            soup.body
        )

        if not main_content:
            return None, links

        # Extract text from meaningful tags
        paragraphs = []
        seen = set()
        for element in main_content.find_all(
            ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th']
        ):
            text = clean_text(element.get_text(separator=' '))
            if len(text) > 30 and text not in seen:
                seen.add(text)
                paragraphs.append(text)

        content = "\n".join(paragraphs)

        # Fallback: if tag-based extraction yields too little, use full text
        # (handles pages where content is in div/span elements, e.g. faculty listings)
        if len(content) < MIN_CONTENT_LEN:
            full_text = main_content.get_text(separator='\n')
            lines = [clean_text(line) for line in full_text.split('\n') if len(clean_text(line)) > 10]
            content = "\n".join(lines)

        if len(content) < MIN_CONTENT_LEN:
            return None, links

        return {
            "url": url,
            "title": title_text,
            "content": content,
        }, links

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] {url}: {e}")
        return None, set()


def discover_from_sitemap():
    """Try to get URLs from sitemap.xml."""
    urls = set()
    try:
        for sitemap_path in ["/sitemap.xml", "/sitemap_index.xml", "/page-sitemap.xml"]:
            sitemap_url = urljoin(BASE_URL, sitemap_path)
            r = requests.get(sitemap_url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and 'xml' in r.headers.get('Content-Type', ''):
                soup = BeautifulSoup(r.text, 'xml')
                for loc in soup.find_all('loc'):
                    u = loc.text.strip()
                    if BASE_URL in u:
                        urls.add(u)
        if urls:
            print(f"  Sitemap: found {len(urls)} URLs")
    except Exception as e:
        print(f"  Sitemap error: {e}")
    return urls


def scrape_college():
    """BFS crawler — visits all internal pages of bvrit.ac.in."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print("=" * 60)
    print("  BVRIT College Website — Full Crawler")
    print("=" * 60)

    # Build initial queue
    queue = deque()
    visited_normalized = set()

    # Add seed URLs
    for path in SEED_URLS:
        url = urljoin(BASE_URL, path)
        norm = normalize_url(url)
        if norm not in visited_normalized:
            visited_normalized.add(norm)
            queue.append(url)

    # Add sitemap URLs
    print("\n[1] Checking sitemap...")
    for url in discover_from_sitemap():
        norm = normalize_url(url)
        if norm not in visited_normalized and not should_skip_url(url):
            visited_normalized.add(norm)
            queue.append(url)

    print(f"  Starting queue: {len(queue)} URLs")

    all_pages = []
    all_text_content = []
    successful = 0
    failed = 0
    total_processed = 0

    print(f"\n[2] Crawling (max {MAX_PAGES} pages)...\n")

    while queue and successful < MAX_PAGES:
        url = queue.popleft()
        total_processed += 1

        if should_skip_url(url):
            continue

        print(f"  [{successful + 1}] {url}")

        result, discovered_links = extract_page_content(url)

        # Enqueue newly discovered internal links
        for link in discovered_links:
            norm = normalize_url(link)
            if norm not in visited_normalized and not should_skip_url(link) and is_internal(link):
                visited_normalized.add(norm)
                queue.append(link)

        if result:
            all_pages.append(result)

            page_text = f"\n{'='*60}\n"
            page_text += f"SOURCE: {result['url']}\n"
            page_text += f"TITLE: {result['title']}\n"
            page_text += f"{'='*60}\n"
            page_text += result['content'] + "\n"
            all_text_content.append(page_text)

            successful += 1
            print(f"      -> OK ({len(result['content'])} chars) | queue: {len(queue)}")
        else:
            failed += 1
            print(f"      -> SKIPPED")

        time.sleep(CRAWL_DELAY)

    # Save plain text
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("BVRIT COLLEGE WEBSITE CONTENT\n")
        f.write(f"Scraped on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: {BASE_URL}\n")
        f.write(f"Pages scraped: {successful}\n")
        f.write("\n".join(all_text_content))

    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_pages, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  CRAWL COMPLETE")
    print(f"  Pages with content : {successful}")
    print(f"  Skipped/failed     : {failed}")
    print(f"  Total URLs seen    : {len(visited_normalized)}")
    print(f"  Text file          : {OUTPUT_FILE}")
    print(f"  JSON file          : {OUTPUT_JSON}")
    print(f"{'='*60}")

    return all_pages


if __name__ == "__main__":
    scrape_college()
