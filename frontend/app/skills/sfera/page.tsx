"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Check,
  Clock,
  Phone,
  Plus,
  Trash2,
  Users,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { api } from "@/lib/api";

interface Person {
  id: string;
  full_name: string;
  phone: string | null;
  email: string | null;
  relationship: string | null;
  last_contact_at: string | null;
  last_contact_channel: string | null;
  target_interval_months: number;
  notes: string | null;
  days_since_last_contact: number | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

const RELATIONSHIPS = [
  { value: "rodina", label: "Rodina" },
  { value: "pritel", label: "Přítel" },
  { value: "byvaly_klient", label: "Bývalý klient" },
  { value: "znamy", label: "Známý" },
  { value: "kolega", label: "Kolega" },
  { value: "jiny", label: "Jiný" },
];

export default function SferaPage() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);

  // Add form
  const [adding, setAdding] = useState(false);
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [rel, setRel] = useState("znamy");

  const load = async () => {
    setLoading(true);
    try {
      const qs = overdueOnly ? "?overdue_only=true" : "";
      setPersons(await api.get<Person[]>(`/sfera/persons${qs}`));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overdueOnly]);

  const add = async () => {
    if (!fullName.trim()) return;
    await api.post<Person>("/sfera/persons", {
      full_name: fullName.trim(),
      phone: phone.trim() || null,
      email: email.trim() || null,
      relationship: rel,
    });
    setFullName("");
    setPhone("");
    setEmail("");
    setAdding(false);
    await load();
  };

  const logContact = async (id: string) => {
    await api.post(`/sfera/persons/${id}/contact`, { channel: "phone" });
    await load();
  };

  const remove = async (id: string) => {
    if (!confirm("Odebrat osobu?")) return;
    await api.delete(`/sfera/persons/${id}`);
    await load();
  };

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-5xl mx-auto px-4 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix mb-4"
        >
          <ArrowLeft size={16} /> Zpět
        </Link>

        <h1 className="text-matrix text-2xl mb-4 tracking-wide flex items-center gap-2">
          <Users size={22} /> Sféra vlivu
        </h1>

        <p className="text-matrix-dim text-sm mb-4">
          Pravidelný kontakt každých 4 měsíců. 🔒 Telefony a e-maily jsou
          šifrované v DB.
        </p>

        {/* Controls */}
        <div className="flex items-center gap-3 flex-wrap mb-4">
          <label className="text-sm text-matrix-dim flex items-center gap-2">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={(e) => setOverdueOnly(e.target.checked)}
              className="accent-matrix-green"
            />
            Jen osoby, které mají překročený interval
          </label>
          <button
            onClick={() => setAdding(!adding)}
            className="inline-flex items-center gap-1 px-3 py-1 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow ml-auto"
          >
            <Plus size={14} /> Přidat osobu
          </button>
        </div>

        {/* Add form */}
        {adding && (
          <div className="bg-matrix-tile p-4 rounded mb-4 space-y-2">
            <input
              type="text"
              placeholder="Jméno a příjmení *"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
            />
            <div className="grid md:grid-cols-2 gap-2">
              <input
                type="tel"
                placeholder="Telefon"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
              />
              <input
                type="email"
                placeholder="E-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
              />
            </div>
            <select
              value={rel}
              onChange={(e) => setRel(e.target.value)}
              className="w-full bg-matrix-bg border border-matrix rounded px-2 py-2 text-matrix text-sm"
            >
              {RELATIONSHIPS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
            <button
              onClick={add}
              className="px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow"
            >
              Uložit
            </button>
          </div>
        )}

        {/* List */}
        {loading && <p className="text-matrix-dim">Načítám…</p>}
        {!loading && persons.length === 0 && (
          <p className="text-matrix-dim italic">
            Zatím prázdné. Přidej přes + tlačítko nahoře.
          </p>
        )}

        <div className="space-y-2">
          {persons.map((p) => (
            <div
              key={p.id}
              className={`bg-matrix-tile p-3 rounded flex items-start gap-3 ${
                p.is_overdue ? "border-l-4 border-yellow-400" : ""
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-matrix font-bold">{p.full_name}</span>
                  {p.relationship && (
                    <span className="text-xs text-matrix-dim px-2 py-0.5 border border-matrix-dim rounded">
                      {RELATIONSHIPS.find((r) => r.value === p.relationship)
                        ?.label || p.relationship}
                    </span>
                  )}
                  {p.is_overdue && (
                    <span className="text-xs text-yellow-400 flex items-center gap-1">
                      <Clock size={10} /> Ozvi se
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-3 text-xs text-matrix-dim mt-1">
                  {p.phone && <span>📞 {p.phone}</span>}
                  {p.email && <span>✉ {p.email}</span>}
                  <span>
                    {p.last_contact_at
                      ? `poslední kontakt před ${p.days_since_last_contact} dny`
                      : "nikdy nekontaktováno"}
                  </span>
                </div>
              </div>

              <button
                onClick={() => logContact(p.id)}
                className="text-green-400 hover:text-green-200 p-1"
                title="Právě jsem kontaktoval"
              >
                <Check size={16} />
              </button>
              <button
                onClick={() => remove(p.id)}
                className="text-matrix-dim hover:text-red-400 p-1"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="sfera"
      />
    </>
  );
}
