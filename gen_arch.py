import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig = plt.figure(figsize=(24, 13))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 24)
ax.set_ylim(0, 13)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

BG  = '#0d1117'
TXT = '#e6edf3'
DIM = '#8b949e'

def box(x, y, w, h, title, subtitle, fc, ec, tc=TXT):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                facecolor=fc, edgecolor=ec, linewidth=2.5, zorder=3))
    if subtitle:
        ax.text(x+w/2, y+h*0.64, title, ha='center', va='center',
                color=tc, fontsize=18, fontweight='bold', zorder=4)
        ax.text(x+w/2, y+h*0.28, subtitle, ha='center', va='center',
                color=tc, fontsize=15, alpha=0.88, zorder=4)
    else:
        ax.text(x+w/2, y+h/2, title, ha='center', va='center',
                color=tc, fontsize=20, fontweight='bold', zorder=4)

def sect(x, y, w, h, label, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                facecolor='#161b2255', edgecolor=ec, linewidth=1.8, zorder=1))
    ax.text(x+w/2, y+h+0.12, label, ha='center', va='bottom',
            color=ec, fontsize=17, fontweight='bold', zorder=2)

def arr(x1, y1, x2, y2, c='#58a6ff', lbl='', rad=0, lx=None, ly=None):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=c, lw=2.2,
                                connectionstyle=f'arc3,rad={rad}'), zorder=5)
    if lbl:
        tx = lx if lx is not None else (x1+x2)/2
        ty = ly if ly is not None else (y1+y2)/2
        ax.text(tx, ty, lbl, ha='center', va='center', color=c, fontsize=16, zorder=6,
                bbox=dict(facecolor=BG, edgecolor='none', alpha=0.92, pad=2))

# ── TITLE ───────────────────────────────────────────────────────────────
ax.text(12, 12.62, 'Real-Time Crypto Streaming & Lakehouse Architecture',
        ha='center', va='center', color=TXT, fontsize=22, fontweight='bold')
ax.text(12, 12.22, 'Coinbase WebSocket  ›  RabbitMQ  ›  PostgreSQL (Medallion)  ›  DuckLake  ›  Metabase',
        ha='center', va='center', color=DIM, fontsize=13)

# ── SECTIONS ────────────────────────────────────────────────────────────
sect(0.3,  9.2,  13.5, 2.5,  '▶  INGESTION & BUFFERING',                      '#8b5cf6')
sect(14.2, 4.7,   9.3, 7.0,  '▶  MEDALLION ARCHITECTURE  (PostgreSQL + dbt)',  '#336791')
sect(14.2, 0.4,   9.3, 3.5,  '▶  LAKEHOUSE & ANALYTICS',                      '#06b6d4')
sect(0.3,  1.0,  13.5, 7.3,  '▶  ORCHESTRATION & INFRASTRUCTURE',             '#017cee')

# ── INGESTION ROW  (boxes h=2.0, center y=10.4) ──────────────────────────
box(0.5,  9.4, 2.8, 2.0, 'Coinbase',  'WebSocket Feed',    '#0052ff18', '#0052ff')
box(3.9,  9.4, 2.8, 2.0, 'Producer',  'Python websockets', '#3776ab18', '#3776ab')
box(7.3,  9.4, 2.8, 2.0, 'RabbitMQ',  'Message Broker',    '#ff660018', '#ff6600')
box(10.7, 9.4, 2.8, 2.0, 'Consumer',  'Python psycopg2',   '#3776ab18', '#3776ab')

arr(3.3,  10.4, 3.9,  10.4, '#8b5cf6', 'JSON')
arr(6.7,  10.4, 7.3,  10.4, '#ff6600', 'AMQP')
arr(10.1, 10.4, 10.7, 10.4, '#ff6600', 'consume')
arr(13.5, 10.4, 14.5, 10.7, '#58a6ff', 'INSERT', lx=13.0, ly=10.85)

# ── MEDALLION LAYERS  h=1.9, gap=0.6 ────────────────────────────────────
# Bronze  9.75 – 11.65
box(14.5, 9.75, 8.9, 1.9,
    'BRONZE  Layer',
    'bronze.raw_trades  ·  Raw JSON payload  ·  Untyped',
    '#b8733318', '#b87333', '#cd9b1d')

arr(18.95, 9.75, 18.95, 9.15, '#10b981')
ax.text(19.4, 9.45, 'dbt run', ha='left', va='center',
        color='#10b981', fontsize=19, fontweight='bold', zorder=9)

# Silver  7.25 – 9.15
box(14.5, 7.25, 8.9, 1.9,
    'SILVER  Layer',
    'silver.trades  ·  Cleaned · Typed · Deduplicated  ·  11 tests',
    '#a8a9ad18', '#a8a9ad')

arr(18.95, 7.25, 18.95, 6.65, '#10b981')
ax.text(19.4, 6.95, 'dbt run', ha='left', va='center',
        color='#10b981', fontsize=19, fontweight='bold', zorder=9)

# Gold  4.75 – 6.65
box(14.5, 4.75, 8.9, 1.9,
    'GOLD  Layer',
    'gold.trade_metrics  ·  Hourly VWAP · Volume · OHLC · buy_ratio  ·  11 tests',
    '#ffd70018', '#ffd700', '#ffd700')

# ── ANALYTICS ROW  h=2.1 ────────────────────────────────────────────────
box(14.5, 0.6, 2.8, 2.7, 'DuckLake Export', 'Python + Pandas',        '#06b6d418', '#06b6d4')
box(18.0, 0.6, 2.6, 2.7, 'DuckDB',          'DuckLake Catalog',       '#ffcd0018', '#ffcd00', '#ffcd00')
box(21.1, 0.6, 2.4, 2.7, 'Metabase',        'BI Dashboard  ·  :3000', '#509ee318', '#509ee3')

arr(17.3, 1.95, 18.0, 1.95, '#06b6d4', 'Parquet')
arr(20.6, 1.95, 21.1, 1.95, '#509ee3', 'SQL')

# Gold → DuckLake
arr(18.95, 4.75, 15.9, 3.3, '#ffd700', 'hourly export', rad=0.25, lx=17.5, ly=4.38)

# ── ORCHESTRATION  left column: big boxes ───────────────────────────────
box(0.5, 5.2, 4.5, 2.8, 'Apache Airflow', 'dbt_hourly_refresh  ·  @hourly', '#017cee18', '#017cee')
box(0.5, 1.5, 4.5, 3.0, 'Docker Compose', '5 services  ·  shared network',  '#2496ed18', '#2496ed')

# Airflow → Silver
arr(5.0, 6.6, 14.5, 8.2, '#017cee', rad=-0.12)

# ── ORCHESTRATION  right column ──────────────────────────────────────────
ax.text(5.5, 7.95, 'Infrastructure', ha='left', va='center',
        color=DIM, fontsize=18, fontweight='bold')
infra = [
    '◆  RabbitMQ 3-management    :5672 / :15672',
    '◆  PostgreSQL 15            :5433',
    '◆  Apache Airflow 2.9.0     :8080',
    '◆  Metabase latest          :3000',
    '◆  DuckDB + DuckLake        local parquet',
]
for i, t in enumerate(infra):
    ax.text(5.5, 7.2 - i*0.78, t, ha='left', va='center', color=DIM, fontsize=16)

ax.text(5.5, 3.6, 'dbt Data Quality Tests', ha='left', va='center',
        color=DIM, fontsize=18, fontweight='bold')
dq = [
    '✓  Bronze · not_null on 6 key columns',
    '✓  Silver · not_null + unique(trade_id) + accepted_values',
    '✓  Gold   · not_null on all 12 aggregation columns',
]
for i, t in enumerate(dq):
    ax.text(5.5, 2.9 - i*0.78, t, ha='left', va='center',
            color='#10b981', fontsize=18)

# ── SAVE ────────────────────────────────────────────────────────────────
plt.savefig('architecture.png', dpi=180, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print('Saved architecture.png')
