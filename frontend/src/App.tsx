import { useCallback, useEffect, useState } from "react";
import { api, setDevUser, type Reservation, type Room, type User } from "./api";
import { UserPicker } from "./components/UserPicker";
import { RoomList } from "./components/RoomList";
import { ReservationForm } from "./components/ReservationForm";
import { ReservationTable } from "./components/ReservationTable";

export default function App() {
  const [users, setUsers] = useState<User[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [mine, setMine] = useState<Reservation[]>([]);
  const [school, setSchool] = useState<Reservation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.devUsers().then(setUsers).catch(() => setError("De API is niet bereikbaar. Draait de backend op poort 8000?"));
  }, []);

  const load = useCallback(async () => {
    try {
      const [r, m, s] = await Promise.all([api.rooms(), api.reservations(true), api.reservations(false)]);
      setRooms(r);
      setMine(m);
      setSchool(s);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Er ging iets mis.");
    }
  }, []);

  function pickUser(picked: User | null) {
    setDevUser(picked?.id ?? null);
    setUser(picked);
    setRooms([]);
    setMine([]);
    setSchool([]);
    if (picked) void load();
  }

  async function cancel(id: number) {
    try {
      await api.cancelReservation(id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Er ging iets mis.");
    }
  }

  return (
    <main>
      <header>
        <h1>Lokalen reserveren</h1>
        <UserPicker users={users} selected={user} onPick={pickUser} />
      </header>

      {error && <p className="error">{error}</p>}

      {!user ? (
        <p className="hint">Kies bovenaan een testgebruiker om te beginnen. Alle gegevens zijn verzonnen.</p>
      ) : (
        <>
          <p className="hint">Je ziet alleen de lokalen en reservaties van {user.school_name}.</p>
          <div className="grid">
            <section className="card">
              <h2>Lokalen</h2>
              <RoomList rooms={rooms} />
            </section>
            <section className="card">
              <h2>Nieuwe reservatie</h2>
              <ReservationForm rooms={rooms} onCreated={load} />
            </section>
          </div>
          <section className="card">
            <h2>Mijn reservaties</h2>
            <ReservationTable reservations={mine} onCancel={cancel} />
          </section>
          <section className="card">
            <h2>Alle reservaties van je school</h2>
            <ReservationTable reservations={school} />
          </section>
        </>
      )}
    </main>
  );
}
