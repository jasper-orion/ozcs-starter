import type { Reservation } from "../api";

interface Props {
  reservations: Reservation[];
  // Zonder onCancel toont de tabel geen annuleerknop.
  onCancel?: (id: number) => void;
}

function formatTime(value: string): string {
  return new Date(value).toLocaleString("nl-BE", { dateStyle: "short", timeStyle: "short" });
}

export function ReservationTable({ reservations, onCancel }: Props) {
  if (reservations.length === 0) return <p className="hint">Nog geen reservaties.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>Lokaal</th>
          <th>Titel</th>
          <th>Van</th>
          <th>Tot</th>
          <th>Door</th>
          {onCancel && <th></th>}
        </tr>
      </thead>
      <tbody>
        {reservations.map((r) => (
          <tr key={r.id}>
            <td>{r.room_name}</td>
            <td>{r.title}</td>
            <td>{formatTime(r.start)}</td>
            <td>{formatTime(r.end)}</td>
            <td>{r.user_display_name}</td>
            {onCancel && (
              <td>
                <button type="button" className="secondary" onClick={() => onCancel(r.id)}>
                  Annuleren
                </button>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
