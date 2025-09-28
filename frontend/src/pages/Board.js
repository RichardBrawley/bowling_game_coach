// src/Board.js
import React, { useMemo, useState } from "react";
import "./Board.css";

export default function Board({ username = "Player" }) {
  // Keep rolls as a flat list for accurate scoring (e.g., [10, 7,3, 9,0, ...])
  const [rolls, setRolls] = useState([]);
  const [coachNote, setCoachNote] = useState("");
  const [loading, setLoading] = useState(false);

  // ---------- Rules & Validation ----------

  // Figure out where the next roll goes and what the max legal pins are.
  // Returns { frame (0..9), ball (0..2), maxPins, gameOver }
  const getNextRollContext = (rs) => {
    let ri = 0;

    // Frames 1..9
    for (let f = 0; f < 9; f++) {
      if (ri >= rs.length) return { frame: f, ball: 0, maxPins: 10, gameOver: false };

      const first = rs[ri];
      if (first === 10) {
        // Strike: frame complete
        ri += 1;
        continue;
      }

      // first exists and not a strike
      if (ri + 1 >= rs.length) {
        // waiting for second ball
        return { frame: f, ball: 1, maxPins: Math.max(0, 10 - first), gameOver: false };
      }

      // two balls present → move on
      ri += 2;
    }

    // Frame 10
    const f = 9;
    if (ri >= rs.length) return { frame: f, ball: 0, maxPins: 10, gameOver: false };

    const a = rs[ri]; // ball 1
    if (a === 10) {
      // Strike on ball 1
      if (ri + 1 >= rs.length) return { frame: f, ball: 1, maxPins: 10, gameOver: false };
      const b = rs[ri + 1]; // ball 2
      if (b === 10) {
        // X X _
        if (ri + 2 >= rs.length) return { frame: f, ball: 2, maxPins: 10, gameOver: false };
        return { frame: f, ball: 3, maxPins: 0, gameOver: true };
      } else {
        // X n _
        if (ri + 2 >= rs.length) {
          // third ball limited by remaining pins after second (open-style)
          return { frame: f, ball: 2, maxPins: Math.max(0, 10 - b), gameOver: false };
        }
        return { frame: f, ball: 3, maxPins: 0, gameOver: true };
      }
    } else {
      // No strike on ball 1
      if (ri + 1 >= rs.length) {
        // waiting for ball 2
        return { frame: f, ball: 1, maxPins: Math.max(0, 10 - a), gameOver: false };
      }
      const b = rs[ri + 1];
      if (a + b === 10) {
        // Spare → one fill ball
        if (ri + 2 >= rs.length) return { frame: f, ball: 2, maxPins: 10, gameOver: false };
        return { frame: f, ball: 3, maxPins: 0, gameOver: true };
      } else {
        // Open 10th → done after two
        return { frame: f, ball: 2, maxPins: 0, gameOver: true };
      }
    }
  };

  // Compute cumulative scores per frame (only when scorable).
  const cumulative = useMemo(() => {
    const out = Array(10).fill(null);
    let ri = 0;
    let total = 0;

    for (let f = 0; f < 10; f++) {
      if (f < 9) {
        if (ri >= rolls.length) break;
        const first = rolls[ri];

        if (first === 10) {
          // Strike → need next two rolls
          if (ri + 2 < rolls.length) {
            total += 10 + (rolls[ri + 1] ?? 0) + (rolls[ri + 2] ?? 0);
            out[f] = total;
          }
          ri += 1;
        } else {
          if (ri + 1 >= rolls.length) break;
          const second = rolls[ri + 1];
          const frameSum = first + second;

          if (frameSum === 10) {
            // Spare → need next one roll
            if (ri + 2 < rolls.length) {
              total += 10 + (rolls[ri + 2] ?? 0);
              out[f] = total;
            }
          } else {
            total += frameSum;
            out[f] = total;
          }
          ri += 2;
        }
      } else {
        // 10th frame
        const a = rolls[ri];
        if (a === undefined) break;
        const b = rolls[ri + 1];
        const c = rolls[ri + 2];

        if (a === 10) {
          if (b === undefined) break;
          if (b === 10) {
            if (c === undefined) break;
            total += 10 + 10 + c;
          } else {
            if (c === undefined) break;
            total += 10 + b + c;
          }
        } else {
          if (b === undefined) break;
          if (a + b === 10) {
            if (c === undefined) break;
            total += 10 + c;
          } else {
            total += a + b;
          }
        }
        out[f] = total;
        break;
      }
    }
    return out;
  }, [rolls]);

  const next = useMemo(() => getNextRollContext(rolls), [rolls]);
  const totalScore = useMemo(
    () => cumulative.reduce((s, v) => s + (typeof v === "number" ? v : 0), 0),
    [cumulative]
  );

  // ---------- Actions ----------
  const handleScoreClick = (pins) => {
    if (next.gameOver) return;
    if (pins < 0 || pins > next.maxPins) return;
    setRolls((prev) => [...prev, pins]);
  };

  const restart = () => {
    setRolls([]);
    setCoachNote("");
  };

  const summarizeViaAPI = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Please login again.");
        return;
      }
      setLoading(true);

      // Build frames payload from rolls
      let ri = 0;
      const frames = [];
      for (let f = 1; f <= 10; f++) {
        if (f < 10) {
          if (rolls[ri] === 10) {
            frames.push({ frame_number: f, roll1: 10, roll2: null, roll3: null, frame_score: null });
            ri += 1;
          } else {
            const a = rolls[ri] ?? null;
            const b = rolls[ri + 1] ?? null;
            frames.push({ frame_number: f, roll1: a, roll2: b, roll3: null, frame_score: null });
            ri += a === null ? 0 : b === null ? 1 : 2;
          }
        } else {
          const a = rolls[ri] ?? null;
          const b = rolls[ri + 1] ?? null;
          const c = rolls[ri + 2] ?? null;
          frames.push({ frame_number: f, roll1: a, roll2: b, roll3: c, frame_score: null });
        }
      }

      const res = await fetch("http://127.0.0.1:8002/summarize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({scores: rolls}),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Summarize failed");
      }

      const data = await res.json();
      setCoachNote(data.feedback);
    } catch (e) {
      setCoachNote("⚠️ " + e.message);
    } finally {
      setLoading(false);
    }
  };

  // ---------- Rendering ----------

  const renderFrames = () => {
    let ri = 0;

    return Array.from({ length: 10 }, (_, f) => {
      let d1 = "", d2 = "", d3 = "";
      let isCurrent = next.frame === f && !next.gameOver;

      if (f < 9) {
        const first = rolls[ri];
        if (first === undefined) {
          // empty frame
        } else if (first === 10) {
          d1 = "X";
          ri += 1;
        } else {
          d1 = String(first);
          const second = rolls[ri + 1];
          if (second !== undefined) {
            d2 = first + second === 10 ? "/" : String(second);
            ri += 2;
          } else {
            // waiting for second
            ri += 1;
          }
        }
      } else {
        // 10th frame
        const a = rolls[ri];
        if (a !== undefined) {
          d1 = a === 10 ? "X" : String(a);
          const b = rolls[ri + 1];
          if (b !== undefined) {
            if (a === 10) d2 = b === 10 ? "X" : String(b);
            else d2 = a + b === 10 ? "/" : String(b);

            const c = rolls[ri + 2];
            if (c !== undefined) {
              if (a === 10) {
                // if b strike, c can be X; else b + c can be spare
                if (b === 10) d3 = c === 10 ? "X" : String(c);
                else d3 = b + c === 10 ? "/" : String(c);
              } else if (a + b === 10) {
                d3 = c === 10 ? "X" : String(c);
              }
            }
          }
        }
      }

      const score = cumulative[f] ?? "";

      return (
        <div key={f} className={`frame ${isCurrent ? "current" : ""}`}>
          <div className="frame-label">Frame {f + 1}</div>
          <div className={`rolls ${f === 9 ? "rolls-10th" : ""}`}>
            <div className={`roll ${d1 === "X" ? "strike" : ""}`}>{d1}</div>
            <div className={`roll ${d2 === "/" ? "spare" : ""} ${d2 === "X" ? "strike" : ""}`}>{d2}</div>
            {f === 9 && (
              <div className={`roll ${d3 === "/" ? "spare" : ""} ${d3 === "X" ? "strike" : ""}`}>{d3}</div>
            )}
          </div>
          <div className="score">{score}</div>
        </div>
      );
    });
  };

  const renderButtons = () => {
    const disabledAll = next.gameOver;
    const max = next.maxPins;

    return (
      <div className="buttons">
        {Array.from({ length: 11 }, (_, i) => (
          <button key={i} onClick={() => handleScoreClick(i)} disabled={disabledAll || i > max}>
            {i}
          </button>
        ))}
        <button className="restart" onClick={restart}>Restart</button>
        {next.gameOver && (
          <button className="summarize" onClick={summarizeViaAPI} disabled={loading}>
            {loading ? "Analyzing…" : "Summarize"}
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="bowling-app">
      <header className="topbar">
        <h1>🎳 Bowling Scoreboard</h1>
        <div className="status">
          <span className="who">Signed in: <strong>{username}</strong></span>
          {next.gameOver ? (
            <strong className="final">Game Over · Final: {totalScore}</strong>
          ) : (
            <>
              <span>Next: <strong>F{next.frame + 1}</strong>·<strong>B{next.ball + 1}</strong></span>
              <span className="range">Allowed: 0–{next.maxPins}</span>
              <span className="total">Total: {totalScore}</span>
            </>
          )}
        </div>
      </header>

      <div className="scoreboard">{renderFrames()}</div>

      {renderButtons()}

      {coachNote && (
        <div className="coach-card">
          <h3>Coach Feedback</h3>
          <pre>{coachNote}</pre>
        </div>
      )}
    </div>
  );
}
