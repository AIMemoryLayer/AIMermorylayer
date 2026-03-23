"use client";

import { motion } from "framer-motion";
import {
  Search,
  Brain,
  Plus,
  Settings,
  History,
  Info,
  Sparkles,
} from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { fetchMemories, createMemory, type MemoryRecord } from "@/lib/api";

export default function Dashboard() {
  const [memories, setMemories] = useState<MemoryRecord[]>([]);
  const [query, setQuery] = useState("");
  const [newContent, setNewContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [ownerId] = useState("default-user");

  const loadMemories = async () => {
    try {
      const data = await fetchMemories(ownerId, query);
      setMemories(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [query]);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    setLoading(true);
    try {
      await createMemory({
        owner_id: ownerId,
        content: newContent,
        metadata: { importance: "medium", type: "manual" },
      });
      setNewContent("");
      loadMemories();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden text-slate-50">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 border-r border-white/10 flex flex-col items-center lg:items-start py-8 px-4 glass">
        <div className="flex items-center gap-3 mb-12 px-2">
          <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400">
            <Brain size={24} />
          </div>
          <span className="hidden lg:block font-bold text-xl tracking-tight">
            AI Memory
          </span>
        </div>

        <nav className="flex-1 space-y-2 w-full">
          <NavItem icon={<History size={20} />} label="Memories" active />
          <NavItem icon={<Sparkles size={20} />} label="Insights" />
          <NavItem icon={<Settings size={20} />} label="Settings" />
        </nav>

        <div className="mt-auto w-full">
          <div className="p-4 rounded-2xl glass-hover cursor-pointer border border-white/5 bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-500/30 border border-indigo-400/30 flex items-center justify-center text-xs font-bold text-indigo-400">
                AD
              </div>
              <div className="hidden lg:block overflow-hidden">
                <p className="text-sm font-medium truncate">Admin User</p>
                <p className="text-xs text-emerald-400 truncate">Online</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Background Accents */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/10 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-cyan-600/5 blur-[100px] rounded-full translate-y-1/3 -translate-x-1/4 pointer-events-none" />

        <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 z-10">
          <div className="relative w-full max-w-md">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
              size={18}
            />
            <input
              type="text"
              placeholder="Search memories neural-style..."
              className="w-full h-11 bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 outline-none focus:ring-2 ring-cyan-500/30 transition-all text-sm"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-2 bg-slate-50 text-slate-950 px-4 py-2 rounded-xl text-sm font-semibold hover:bg-white transition-all">
            <Plus size={18} />
            <span className="hidden sm:inline">Add Connection</span>
          </button>
        </header>

        <section className="flex-1 overflow-y-auto p-8 space-y-8 z-10 custom-scrollbar">
          {/* Hero Ingestion Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-4xl mx-auto p-6 rounded-3xl glass border-white/20 bg-linear-to-br from-white/10 to-transparent"
          >
            <form onSubmit={handleIngest} className="space-y-4">
              <div className="flex items-center gap-2 text-cyan-400 mb-2">
                <Sparkles size={16} />
                <span className="text-xs font-bold uppercase tracking-widest">
                  Thought Ingestion
                </span>
              </div>
              <textarea
                className="w-full bg-transparent border-none outline-none text-xl resize-none placeholder:text-slate-500 min-h-[100px]"
                placeholder="What's on your mind today? Let the AI remember it..."
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
              />
              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <div className="flex gap-2">
                  <Tag label="Personal" color="cyan" />
                  <Tag label="High Importance" color="indigo" />
                </div>
                <button
                  disabled={loading}
                  className={cn(
                    "px-6 py-2 rounded-xl text-sm font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-400/30 hover:bg-cyan-500/30 transition-all",
                    loading && "opacity-50 cursor-not-allowed",
                  )}
                >
                  {loading ? "Neuralizing..." : "Store Memory"}
                </button>
              </div>
            </form>
          </motion.div>

          {/* Memory Feed */}
          <div className="max-w-4xl mx-auto space-y-6">
            <h2 className="text-lg font-semibold flex items-center gap-2 px-2">
              Recent Memories
              <span className="text-xs font-normal text-slate-500 bg-white/5 px-2 py-0.5 rounded-full">
                {memories.length}
              </span>
            </h2>

            <div className="grid gap-4">
              {memories.length > 0 ? (
                memories.map((m, i) => (
                  <motion.div
                    key={m.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="p-5 rounded-2xl glass glass-hover cursor-pointer group"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-tighter text-cyan-400 opacity-70">
                        {m.metadata.type || "Generic"}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        {new Date().toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-slate-200 leading-relaxed font-medium">
                      {m.content}
                    </p>
                    <div className="mt-4 flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="text-xs text-slate-400 hover:text-cyan-400">
                        View Details
                      </button>
                      <button className="text-xs text-slate-400 hover:text-red-400">
                        Forget
                      </button>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="py-20 flex flex-col items-center text-center space-y-4">
                  <div className="p-4 rounded-full bg-white/5 text-slate-600">
                    <Info size={32} />
                  </div>
                  <div>
                    <p className="font-semibold">No Neural Links Found</p>
                    <p className="text-sm text-slate-500">
                      Start by adding a thought above.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active = false,
}: {
  icon: any;
  label: string;
  active?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 p-3 rounded-2xl transition-all cursor-pointer group",
        active
          ? "bg-cyan-500/10 text-cyan-400 border border-cyan-400/20 shadow-[0_0_15px_rgba(34,211,238,0.1)]"
          : "text-slate-400 hover:bg-white/5 hover:text-slate-200",
      )}
    >
      {icon}
      <span className="hidden lg:block text-sm font-medium">{label}</span>
    </div>
  );
}

function Tag({ label, color }: { label: string; color: "cyan" | "indigo" }) {
  const colors = {
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
  };
  return (
    <span
      className={cn(
        "px-2 py-0.5 rounded-lg text-[10px] font-bold border",
        colors[color],
      )}
    >
      {label}
    </span>
  );
}
