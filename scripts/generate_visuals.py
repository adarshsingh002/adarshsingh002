#!/usr/bin/env python3
"""
generate_visuals.py
===================
Automated Profile Visuals & Milestone Sync Engine for Adarsh Kumar Singh.
- Generates assets/hero_banner.svg with pure CSS @keyframes animations.
- Fetches real-time stats from LeetCode GraphQL & Codeforces (with milestones.json fallback).
- Renders high-DPI, dark-mode SVG vector plots (rating_trend.svg, dsa_breakdown.svg).
- Updates the <!-- ACHIEVEMENTS:START --> ... <!-- ACHIEVEMENTS:END --> block in README.md.
"""

import json
import os
import sys
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(WORKSPACE_DIR, "data", "milestones.json")
ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")
README_PATH = os.path.join(WORKSPACE_DIR, "README.md")

os.makedirs(ASSETS_DIR, exist_ok=True)

def load_milestones():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_leetcode_stats(username, fallback_cp):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      userContestRanking(username: $username) {
        rating
        globalRanking
        topPercentage
        badge {
          name
        }
      }
    }
    """
    try:
        resp = requests.post(
            url,
            json={"query": query, "variables": {"username": username}},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            user_data = data.get("matchedUser")
            contest_data = data.get("userContestRanking")

            stats = fallback_cp["leetcode"].copy()
            if contest_data and contest_data.get("rating"):
                stats["rating"] = round(contest_data["rating"])
                if contest_data.get("badge") and contest_data["badge"].get("name"):
                    stats["badge"] = contest_data["badge"]["name"]
            if user_data and user_data.get("submitStats"):
                subs = user_data["submitStats"].get("acSubmissionNum", [])
                for item in subs:
                    diff = item.get("difficulty", "").lower()
                    cnt = item.get("count", 0)
                    if diff in ["easy", "medium", "hard"]:
                        stats["breakdown"][diff] = cnt
                stats["total_solved"] = sum(stats["breakdown"].values())
            print(f"[*] Fetched live LeetCode telemetry for {username}")
            return stats
    except Exception as e:
        print(f"[!] LeetCode API exception: {e}. Utilizing fallback data.")
    return fallback_cp["leetcode"]

def fetch_codeforces_stats(username, fallback_cf):
    try:
        url = f"https://codeforces.com/api/user.info?handles={username}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("result"):
                u = data["result"][0]
                return {
                    "rating": u.get("rating", fallback_cf["rating"]),
                    "rank": u.get("rank", fallback_cf["rank"]).title(),
                    "max_rating": u.get("maxRating", fallback_cf["max_rating"])
                }
    except Exception as e:
        print(f"[!] Codeforces API exception: {e}. Utilizing fallback.")
    return fallback_cf

def generate_hero_banner():
    """Generates a modern CSS keyframe-animated SVG hero banner."""
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="100%" height="100%">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050811" />
      <stop offset="50%" stop-color="#0b1329" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>

    <linearGradient id="cyan-glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#818cf8" />
      <stop offset="100%" stop-color="#c084fc" />
    </linearGradient>

    <linearGradient id="wire-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="rgba(56, 189, 248, 0.15)" />
      <stop offset="50%" stop-color="rgba(129, 140, 248, 0.4)" />
      <stop offset="100%" stop-color="rgba(192, 132, 252, 0.15)" />
    </linearGradient>

    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>

    <style>
      @keyframes floatParticle1 {
        0% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
        50% { transform: translateY(-30px) translateX(20px); opacity: 0.8; }
        100% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
      }
      @keyframes floatParticle2 {
        0% { transform: translateY(0px) translateX(0px); opacity: 0.2; }
        50% { transform: translateY(-40px) translateX(-25px); opacity: 0.7; }
        100% { transform: translateY(0px) translateX(0px); opacity: 0.2; }
      }
      @keyframes waveAnimation {
        0% { transform: translateX(0); }
        50% { transform: translateX(-40px); }
        100% { transform: translateX(0); }
      }
      @keyframes pulseGlow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; filter: drop-shadow(0 0 12px rgba(56,189,248,0.7)); }
      }
      .particle-1 { animation: floatParticle1 6s ease-in-out infinite; }
      .particle-2 { animation: floatParticle2 8s ease-in-out infinite; }
      .wave-path { animation: waveAnimation 10s ease-in-out infinite; }
      .title-text {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
      }
      .mono-text {
        font-family: 'Fira Code', 'Courier New', monospace;
      }
      .tag-pill {
        animation: pulseGlow 4s ease-in-out infinite;
      }
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="320" rx="16" fill="url(#bg-grad)" stroke="#1e293b" stroke-width="2"/>

  <!-- Subtle Cyber Grid -->
  <g stroke="rgba(255, 255, 255, 0.03)" stroke-width="1">
    <line x1="100" y1="0" x2="100" y2="320"/>
    <line x1="250" y1="0" x2="250" y2="320"/>
    <line x1="400" y1="0" x2="400" y2="320"/>
    <line x1="550" y1="0" x2="550" y2="320"/>
    <line x1="700" y1="0" x2="700" y2="320"/>
    <line x1="850" y1="0" x2="850" y2="320"/>
    <line x1="1000" y1="0" x2="1000" y2="320"/>
    <line x1="0" y1="80" x2="1200" y2="80"/>
    <line x1="0" y1="160" x2="1200" y2="160"/>
    <line x1="0" y1="240" x2="1200" y2="240"/>
  </g>

  <!-- Wave Accent Curves -->
  <path class="wave-path" d="M-50,230 Q 300,140 600,240 T 1250,190" fill="none" stroke="url(#wire-grad)" stroke-width="2.5" />
  <path class="wave-path" d="M-30,260 Q 250,180 650,280 T 1250,220" fill="none" stroke="url(#wire-grad)" stroke-width="1.5" />

  <!-- Floating Particles -->
  <circle class="particle-1" cx="220" cy="110" r="3" fill="#38bdf8" />
  <circle class="particle-2" cx="380" cy="70" r="2.5" fill="#818cf8" />
  <circle class="particle-1" cx="890" cy="90" r="3.5" fill="#c084fc" />
  <circle class="particle-2" cx="1020" cy="180" r="2.5" fill="#38bdf8" />
  <circle class="particle-1" cx="150" cy="220" r="2" fill="#818cf8" />
  <circle class="particle-2" cx="720" cy="60" r="3" fill="#38bdf8" />

  <!-- macOS Top Control Dots -->
  <g transform="translate(30, 26)">
    <circle cx="0" cy="0" r="6" fill="#ff5f56"/>
    <circle cx="20" cy="0" r="6" fill="#ffbd2e"/>
    <circle cx="40" cy="0" r="6" fill="#27c93f"/>
    <text x="65" y="4" fill="#64748b" class="mono-text" font-size="12">system://cluster/adarsh-kumar-singh</text>
  </g>

  <!-- Status Pill Top Right -->
  <g transform="translate(940, 22)" class="tag-pill">
    <rect width="230" height="26" rx="13" fill="#0f172a" stroke="#38bdf8" stroke-width="1.2"/>
    <circle cx="16" cy="13" r="4.5" fill="#10b981"/>
    <text x="30" y="17" fill="#f8fafc" class="mono-text" font-size="11" font-weight="600">PRODUCTION ACTIVE // 2026</text>
  </g>

  <!-- Hero Identity Content -->
  <g transform="translate(60, 130)">
    <text class="title-text" font-size="44" fill="#ffffff">
      Adarsh Kumar Singh
    </text>
    <text y="38" class="title-text" font-size="20" fill="url(#cyan-glow)" font-weight="600">
      Full-Stack Engineer  •  ML Systems Builder  •  Competitive Programmer
    </text>
    <text y="78" class="mono-text" font-size="14" fill="#94a3b8">
      $ pipeline: [FastAPI, PyTorch, pgvector, Gemini Flash, XGBoost, Docker]
    </text>
    <text y="104" class="mono-text" font-size="13" fill="#64748b">
      &gt; B.E. ISE @ MSRIT Bengaluru (CGPA: 9.46) | LeetCode Knight (1818) | 850+ Solved
    </text>
  </g>

  <!-- Interactive Terminal Badge (Bottom Right) -->
  <g transform="translate(860, 175)">
    <rect width="280" height="96" rx="10" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
    <text x="18" y="28" fill="#38bdf8" class="mono-text" font-size="12" font-weight="700">KERNEL TELEMETRY</text>
    <text x="18" y="50" fill="#e2e8f0" class="mono-text" font-size="12">LC Knight: 1818 (Top 5%)</text>
    <text x="18" y="68" fill="#e2e8f0" class="mono-text" font-size="12">Contest Rank: 914 / 45,000+</text>
    <text x="18" y="86" fill="#10b981" class="mono-text" font-size="11">● All microservices operational</text>
  </g>
</svg>"""
    banner_path = os.path.join(ASSETS_DIR, "hero_banner.svg")
    with open(banner_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[*] Generated animated SVG hero banner -> {banner_path}")

def generate_rating_trend_plot(history, current_rating):
    """Renders dark-mode SVG chart of LeetCode contest trajectory."""
    labels = [h["contest"] for h in history]
    ratings = [h["rating"] for h in history]

    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor="#0d1117")
    ax.set_facecolor("#161b22")

    x = np.arange(len(labels))

    # Gradient-like area under curve
    ax.plot(x, ratings, color="#38bdf8", linewidth=3, marker="o", markersize=7,
            markerfacecolor="#0284c7", markeredgecolor="#e0f2fe", markeredgewidth=2, zorder=4)
    ax.fill_between(x, ratings, min(ratings)-50, color="#38bdf8", alpha=0.15, zorder=2)

    # Annotate points
    for i, txt in enumerate(ratings):
        ax.annotate(
            str(txt),
            (x[i], ratings[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontsize=10,
            fontweight='bold',
            color="#f8fafc" if i == len(ratings)-1 else "#94a3b8"
        )

    # Threshold horizontal line for Knight tier (approx 1750-1800)
    ax.axhline(1800, color="#f59e0b", linestyle="--", linewidth=1.2, alpha=0.7, label="Knight Cutoff (~1800)")

    ax.set_title("LeetCode Contest Rating Trajectory (Peak: 1818)", fontsize=13, fontweight='bold', color="#f8fafc", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight='600', color="#94a3b8")
    ax.set_ylim(min(ratings)-40, max(ratings)+60)
    ax.set_ylabel("Contest Rating", fontsize=10, fontweight='bold', color="#94a3b8")
    ax.tick_params(colors="#94a3b8", which='both')

    # Minimal dark grid
    ax.grid(True, linestyle=":", alpha=0.25, color="#64748b", zorder=1)
    for spine in ax.spines.values():
        spine.set_color("#30363d")

    legend = ax.legend(facecolor="#0d1117", edgecolor="#30363d", labelcolor="#cbd5e1", fontsize=9, loc="upper left")
    plt.tight_layout()

    out_path = os.path.join(ASSETS_DIR, "rating_trend.svg")
    plt.savefig(out_path, format="svg", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"[*] Generated rating trend SVG -> {out_path}")

def generate_dsa_breakdown_plot(breakdown, total_solved):
    """Renders dark-mode SVG bar chart of DSA problems solved by tier."""
    categories = ["Easy (Fundamentals)", "Medium (Core Dynamic/Trees)", "Hard (Advanced Graph/Flow)"]
    counts = [breakdown["easy"], breakdown["medium"], breakdown["hard"]]
    colors = ["#10b981", "#f59e0b", "#ef4444"]

    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor="#0d1117")
    ax.set_facecolor("#161b22")

    x = np.arange(len(categories))
    bars = ax.bar(x, counts, color=colors, width=0.55, edgecolor="#30363d", linewidth=1.5, zorder=3)

    for bar, count in zip(bars, counts):
        yval = bar.get_height()
        pct = (count / total_solved) * 100
        ax.text(
            bar.get_x() + bar.get_width()/2.0,
            yval + 14,
            f"{count} ({pct:.1f}%)",
            ha='center',
            va='bottom',
            fontsize=10.5,
            fontweight='bold',
            color="#f8fafc"
        )

    ax.set_title(f"DSA Problem Breakdown (Total: {total_solved}+ Solved)", fontsize=13, fontweight='bold', color="#f8fafc", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9.5, fontweight='600', color="#94a3b8")
    ax.set_ylim(0, max(counts) + 75)
    ax.set_ylabel("Problems Solved", fontsize=10, fontweight='bold', color="#94a3b8")
    ax.tick_params(colors="#94a3b8", which='both')

    ax.grid(axis='y', linestyle=":", alpha=0.25, color="#64748b", zorder=1)
    for spine in ax.spines.values():
        spine.set_color("#30363d")

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "dsa_breakdown.svg")
    plt.savefig(out_path, format="svg", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"[*] Generated DSA breakdown SVG -> {out_path}")

def update_readme_achievements(data, cp_stats, cf_stats):
    """Parses data and writes clean injected tables between comment anchors."""
    if not os.path.exists(README_PATH):
        print(f"[!] README.md not found at {README_PATH}")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- ACHIEVEMENTS:START -->"
    end_tag = "<!-- ACHIEVEMENTS:END -->"

    if start_tag not in content or end_tag not in content:
        print("[!] Anchor tags not found in README.md")
        return

    # Build Hackathon Rows
    hackathon_rows = ""
    for h in data.get("hackathons", []):
        hackathon_rows += f"""  <tr>
    <td><b>{h['name']}</b></td>
    <td>{h['organizer']}</td>
    <td><code style="color: #38bdf8;">{h['placement']}</code></td>
    <td>{h['domain']}</td>
  </tr>\n"""

    # Build Certification Items
    cert_items = ""
    for c in data.get("certifications", []):
        cert_items += f"- **{c['title']}** — *{c['issuer']}* ({c['year']})\n"

    injected_body = f"""{start_tag}
### 🏆 Verified Honors & Continuous Integration Record

<details open>
  <summary><b>🎯 Invitational Hackathons & Competitive Honors</b></summary>
  <br/>
<table width="100%" cellspacing="0" cellpadding="6">
  <thead>
    <tr bgcolor="#161b22">
      <th align="left">Event</th>
      <th align="left">Organizer</th>
      <th align="left">Standing / Recognition</th>
      <th align="left">Domain Focus</th>
    </tr>
  </thead>
  <tbody>
{hackathon_rows}  </tbody>
</table>
</details>

<details>
  <summary><b>📜 Academic Standing & Specializations</b></summary>
  <br/>

- **B.E. in Information Science & Engineering:** M.S. Ramaiah Institute of Technology (MSRIT), Bengaluru — **CGPA: {data['profile']['education']['cgpa']}**
{cert_items}
</details>

<details open>
  <summary><b>⚡ Live Competitive Stats (Synced via GitHub Actions)</b></summary>
  <br/>

| Platform | Rating / Division | Global Placement | Total Volume |
| :--- | :--- | :--- | :--- |
| **LeetCode** (`{data['profile']['leetcode_handle']}`) | <kbd>Knight: {cp_stats['rating']}</kbd> | **{cp_stats.get('global_rank', 'Top 5% Global')}** | **{cp_stats['total_solved']}+ Solved** |
| **Codeforces** (`{data['profile']['codeforces_handle']}`) | <kbd>{cf_stats['rank']}: {cf_stats['rating']}</kbd> | **Max Rating: {cf_stats['max_rating']}** | Active Competitor |

</details>
{end_tag}"""

    before = content.split(start_tag)[0]
    after = content.split(end_tag)[1]
    new_content = before + injected_body + after

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[*] Synchronized achievements block in README.md")

def main():
    print("[+] Starting Profile Visuals & Milestone Generation Engine...")
    milestones = load_milestones()
    prof = milestones.get("profile", {})
    cp = milestones.get("competitive_programming", {})

    # Live telemetry with fallback
    lc_stats = fetch_leetcode_stats(prof.get("leetcode_handle", "Adarsh_002"), cp)
    cf_stats = fetch_codeforces_stats(prof.get("codeforces_handle", "Adarsh_002"), cp.get("codeforces", {}))

    # Generate visual assets
    generate_hero_banner()
    generate_rating_trend_plot(lc_stats["rating_history"], lc_stats["rating"])
    generate_dsa_breakdown_plot(lc_stats["breakdown"], lc_stats["total_solved"])

    # Synchronize achievements into README
    update_readme_achievements(milestones, lc_stats, cf_stats)
    print("[✔] Profile asset compilation complete.")

if __name__ == "__main__":
    main()

