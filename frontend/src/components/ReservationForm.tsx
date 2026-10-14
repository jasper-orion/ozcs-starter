import { useState, type FormEvent } from "react";
import { api, type Room } from "../api";

interface Props {
  rooms: Room[];
  onCreated: () => Promise<void>;
}

export function ReservationForm({ rooms, onCreated }: Props) {
  const [roomId, setRoomId] = useState("");
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [error, setError] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    try {
      await api.createReservation({ room_id: Number(roomId), title, start, end });
      setTitle("");
      setError("");
      await onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Er ging iets mis.");
    }
  }

  return (
    <form onSubmit={submit}>
      <label>
        Lokaal
        <select required value={roomId} onChange={(e) => setRoomId(e.target.value)}>
          <option value="">Kies een lokaal...</option>
          {rooms.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Titel
        <input required minLength={3} maxLength={100} value={title} onChange={(e) => setTitle(e.target.value)} />
      </label>
      <label>
        Van
        <input required type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} />
      </label>
      <label>
        Tot
        <input required type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Reserveren</button>
    </form>
  );
}
