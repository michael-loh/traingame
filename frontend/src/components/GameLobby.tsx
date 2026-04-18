import React, { useState } from "react";
import { useGame } from "../context/GameContext";

export const GameLobby: React.FC = () => {
  const { setGameId, setPlayerId, setToken, gameState, gameId, playerId, storedGameId } = useGame();
  
  // Local state for UI flow
  const [inputName, setInputName] = useState("");
  const [manualCode, setManualCode] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateGame = async () => {
    setIsCreating(true);
    try {
      const res = await fetch("http://localhost:8000/games", { method: "POST" });
      const data = await res.json();
      setGameId(data.game_id);
    } catch (err) {
      console.error("Failed to create game", err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinGame = async () => {
    if (!gameId || !inputName) return;
    try {
      const res = await fetch(`http://localhost:8000/games/${gameId}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: inputName }),
      });
      const data = await res.json();
      if (res.ok) {
        setPlayerId(data.player_id);
        setToken(data.secret_token);
      } else {
        alert(data.detail || "Failed to join");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartGame = async () => {
    if (!gameId) return;
    await fetch(`http://localhost:8000/games/${gameId}/start`, { method: "POST" });
  };

  const shareUrl = `${window.location.origin}${window.location.pathname}?game=${gameId}`;

  // --- VIEW 1: LANDING (No Game ID selected yet) ---
  if (!gameId) {
    return (
      <div className="max-w-sm w-full bg-slate-900 rounded-[2.5rem] p-10 shadow-2xl border border-slate-800 flex flex-col gap-8 text-center">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter">TRAIN GAME</h1>
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest mt-2">Ready to play?</p>
        </div>

        <div className="flex flex-col gap-4">
          <button
            onClick={handleCreateGame}
            disabled={isCreating}
            className="w-full py-5 bg-indigo-600 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/20 hover:bg-indigo-500 transition-all active:scale-95 uppercase tracking-widest text-sm"
          >
            {isCreating ? "Creating..." : "Create Private Room"}
          </button>

          {storedGameId && (
            <button
              onClick={() => setGameId(storedGameId)}
              className="w-full py-4 bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 font-bold rounded-2xl hover:bg-emerald-600/30 transition-all active:scale-95 uppercase tracking-widest text-[10px]"
            >
              Resume Last Session ({storedGameId})
            </button>
          )}
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-800"></div></div>
          <div className="relative flex justify-center text-[10px]"><span className="px-3 bg-slate-900 text-slate-600 font-black uppercase tracking-widest">OR</span></div>
        </div>

        <div className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="ENTER ROOM CODE"
            value={manualCode}
            onChange={(e) => setManualCode(e.target.value.toUpperCase())}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-center text-white font-mono font-bold placeholder:text-slate-700 focus:border-indigo-500 outline-none transition-colors"
          />
          <button
            onClick={() => setGameId(manualCode)}
            disabled={!manualCode}
            className="w-full py-3 bg-slate-800 text-slate-300 font-bold rounded-xl hover:bg-slate-700 disabled:opacity-30 transition-all uppercase text-[10px] tracking-widest"
          >
            Join Existing
          </button>
        </div>
      </div>
    );
  }

  // --- VIEW 2: ROOM LOBBY (Game ID exists, but maybe not joined yet) ---
  const isJoined = !!gameState?.players[playerId || ""];
  const isHost = gameState?.turn_order[0] === playerId;

  return (
    <div className="max-w-md w-full bg-slate-900 rounded-[2.5rem] p-10 shadow-2xl border border-slate-800 flex flex-col gap-8">
      <div className="text-center">
        <h2 className="text-2xl font-black text-white tracking-tight">Lobby: {gameId}</h2>
        <div 
          onClick={() => { navigator.clipboard.writeText(shareUrl); alert("Link Copied!"); }}
          className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:border-slate-600 transition-all group"
        >
          <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Share Invitation Link</p>
          <p className="text-[10px] font-mono text-indigo-400 truncate group-hover:text-indigo-300">{shareUrl}</p>
        </div>
      </div>

      {!isJoined ? (
        <div className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="YOUR NAME"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-5 py-4 text-white font-bold placeholder:text-slate-700 focus:border-indigo-500 outline-none transition-colors"
          />
          <button
            onClick={handleJoinGame}
            disabled={!inputName}
            className="w-full py-5 bg-indigo-600 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/20 hover:bg-indigo-500 transition-all active:scale-95 uppercase tracking-widest text-sm"
          >
            Join Lobby
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          <div className="space-y-3">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Players Ready</h3>
            <div className="grid grid-cols-1 gap-2">
              {Object.keys(gameState?.players || {}).map((pId) => (
                <div key={pId} className="bg-slate-950 border border-slate-800 p-4 rounded-2xl flex justify-between items-center">
                  <span className="text-white font-bold">{pId}</span>
                  {gameState?.turn_order[0] === pId && (
                    <span className="text-[8px] font-black text-indigo-400 border border-indigo-400/30 px-2 py-0.5 rounded-full uppercase">Host</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {isHost ? (
            <button
              onClick={handleStartGame}
              className="w-full py-5 bg-indigo-600 text-white font-black rounded-2xl shadow-xl shadow-indigo-500/20 hover:bg-indigo-500 transition-all active:scale-95 uppercase tracking-widest text-sm"
            >
              Start Game session
            </button>
          ) : (
            <div className="py-4 text-center">
               <p className="text-slate-500 text-xs font-bold animate-pulse">Waiting for host to start...</p>
            </div>
          )}
        </div>
      )}
      
      <button 
        onClick={() => { 
          setGameId(""); 
          setPlayerId(""); 
          setToken("");
          localStorage.removeItem("train_game_id");
          localStorage.removeItem("train_player_id");
          localStorage.removeItem("train_token");
          window.history.pushState({}, '', window.location.pathname); 
        }}
        className="text-[9px] font-black text-slate-600 hover:text-slate-400 uppercase tracking-widest transition-colors"
      >
        Leave Room
      </button>
    </div>
  );
};
