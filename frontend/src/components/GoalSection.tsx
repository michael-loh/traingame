import React from "react";
import { useGame } from "../context/GameContext";

export const GoalSection: React.FC = () => {
  const { gameState, playerId, setHoveredGoal } = useGame();

  if (!gameState || !playerId) return null;

  const player = gameState.players[playerId];
  if (!player) return null;

  return (
    <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700 h-full flex flex-col shadow-lg overflow-hidden">
      <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Your Goals</h2>
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
        {player.goals.map((goal) => (
          <div
            key={goal.id}
            onMouseEnter={() => setHoveredGoal({ node_a: goal.node_a, node_b: goal.node_b })}
            onMouseLeave={() => setHoveredGoal(null)}
            className={`px-3 py-2 rounded-xl border transition-all cursor-help ${
              goal.is_completed 
                ? "bg-green-500/10 border-green-500/50 text-green-400" 
                : "bg-slate-900 border-slate-700 text-slate-300 hover:border-indigo-500/50"
            }`}
          >
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-bold uppercase truncate pr-2">
                {gameState.cities[goal.node_a]?.name || goal.node_a} - {gameState.cities[goal.node_b]?.name || goal.node_b}
              </span>
              <span className="text-[10px] font-black ml-2">{goal.points}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
