import './mascot.css'

/**
 * Applio — the Appliora assistant mascot.
 *
 * moods: idle | waving | searching | happy | sad
 * Pure SVG + CSS keyframes, no assets or libraries.
 */
export default function Mascot({ mood = 'idle', message = '' }) {
  return (
    <div className={`mascot mood-${mood}`} role="status" aria-live="polite">
      {message && (
        <div className="mascot-bubble" key={message}>
          {message}
        </div>
      )}
      <svg
        className="mascot-svg"
        viewBox="0 0 120 130"
        width="96"
        height="104"
        aria-label={`Applio the assistant is ${mood}`}
      >
        {/* shadow */}
        <ellipse className="m-shadow" cx="60" cy="122" rx="26" ry="5" fill="#1c1e26" opacity="0.12" />

        <g className="m-body-group">
          {/* antenna */}
          <g className="m-antenna">
            <line x1="60" y1="22" x2="60" y2="10" stroke="#4f46e5" strokeWidth="3" strokeLinecap="round" />
            <circle className="m-antenna-tip" cx="60" cy="7" r="4.5" fill="#f59e0b" />
          </g>

          {/* left arm (waves) */}
          <g className="m-arm-left">
            <path
              d="M30 72 Q16 66 14 52"
              fill="none"
              stroke="#4f46e5"
              strokeWidth="7"
              strokeLinecap="round"
            />
            <circle cx="14" cy="50" r="6" fill="#6366f1" />
          </g>

          {/* right arm (holds magnifier while searching) */}
          <g className="m-arm-right">
            <path
              d="M90 72 Q102 78 105 90"
              fill="none"
              stroke="#4f46e5"
              strokeWidth="7"
              strokeLinecap="round"
            />
            <circle cx="105" cy="92" r="6" fill="#6366f1" />
            <g className="m-magnifier">
              <circle cx="105" cy="76" r="9" fill="none" stroke="#f59e0b" strokeWidth="3.5" />
              <line x1="105" y1="85" x2="105" y2="94" stroke="#f59e0b" strokeWidth="3.5" strokeLinecap="round" />
            </g>
          </g>

          {/* body */}
          <rect x="28" y="22" width="64" height="66" rx="20" fill="#4f46e5" />
          <rect x="34" y="28" width="52" height="42" rx="14" fill="#eef0ff" />

          {/* face */}
          <g className="m-face">
            <g className="m-eyes">
              <circle className="m-eye" cx="48" cy="46" r="5" fill="#1c1e26" />
              <circle className="m-eye" cx="72" cy="46" r="5" fill="#1c1e26" />
              {/* closed-eye arcs (sad) */}
              <path className="m-eye-sad" d="M43 46 q5 4 10 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
              <path className="m-eye-sad" d="M67 46 q5 4 10 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
              {/* happy arcs ^^ */}
              <path className="m-eye-happy" d="M43 47 q5 -6 10 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
              <path className="m-eye-happy" d="M67 47 q5 -6 10 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
            </g>
            {/* cheeks */}
            <circle className="m-cheek" cx="42" cy="55" r="3.5" fill="#fca5a5" opacity="0.7" />
            <circle className="m-cheek" cx="78" cy="55" r="3.5" fill="#fca5a5" opacity="0.7" />
            {/* mouths — one per mood */}
            <path className="m-mouth m-mouth-idle" d="M53 59 q7 4 14 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
            <ellipse className="m-mouth m-mouth-happy" cx="60" cy="60" rx="7" ry="5" fill="#1c1e26" />
            <path className="m-mouth m-mouth-sad" d="M53 63 q7 -5 14 0" fill="none" stroke="#1c1e26" strokeWidth="2.5" strokeLinecap="round" />
            <circle className="m-mouth m-mouth-o" cx="60" cy="61" r="3.5" fill="#1c1e26" />
          </g>

          {/* belly light */}
          <circle className="m-belly" cx="60" cy="79" r="4.5" fill="#a5b4fc" />

          {/* legs */}
          <rect x="42" y="86" width="10" height="16" rx="5" fill="#4338ca" />
          <rect x="68" y="86" width="10" height="16" rx="5" fill="#4338ca" />
        </g>

        {/* celebration sparkles (happy) */}
        <g className="m-sparkles" fill="#f59e0b">
          <path className="m-spark s1" d="M20 30 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2 z" />
          <path className="m-spark s2" d="M98 24 l1.6 4 4 1.6 -4 1.6 -1.6 4 -1.6 -4 -4 -1.6 4 -1.6 z" />
          <path className="m-spark s3" d="M104 52 l1.4 3.5 3.5 1.4 -3.5 1.4 -1.4 3.5 -1.4 -3.5 -3.5 -1.4 3.5 -1.4 z" />
        </g>
      </svg>
    </div>
  )
}
