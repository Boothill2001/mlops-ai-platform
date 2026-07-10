// Validated dark-surface chart palette.
// Categorical slots are assigned in fixed order — never cycled or re-ranked.
export const SERIES = {
  blue: '#3987e5',
  aqua: '#199e70',
  yellow: '#c98500',
  green: '#008300',
  violet: '#9085e9',
  red: '#e66767',
} as const;

export const CATEGORICAL: string[] = [
  SERIES.blue,
  SERIES.aqua,
  SERIES.yellow,
  SERIES.green,
  SERIES.violet,
  SERIES.red,
];

// Status colors — reserved for state, never used as "series N".
export const STATUS = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
} as const;

// Sequential blue ramp (light -> dark) for magnitude encodings.
export const SEQUENTIAL_BLUE = ['#cde2fb', '#86b6ef', '#3987e5', '#1c5cab', '#12406f'];

export const CHART_TEXT = '#94a3b8'; // slate-400 — recessive axis/label ink
export const CHART_GRID = '#334155'; // slate-700 — recessive grid
export const TOOLTIP_STYLE = {
  backgroundColor: '#0f172a',
  border: '1px solid #334155',
  borderRadius: '8px',
  color: '#e2e8f0',
  fontSize: '12px',
} as const;
