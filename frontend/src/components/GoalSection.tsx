import React from "react";
import { useGame } from "../context/GameContext";

export const GoalSection: React.FC = () => {
  const { gameState, playerId } = useGame();

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
            className={`px-3 py-2 rounded-xl border transition-colors ${
              goal.is_completed 
                ? "bg-green-500/10 border-green-500/50 text-green-400" 
                : "bg-slate-900 border-slate-700 text-slate-300"
            }`}
          >
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-bold uppercase truncate">{goal.node_a} - {goal.node_b}</span>
              <span className="text-[10px] font-black ml-2">{goal.points}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
