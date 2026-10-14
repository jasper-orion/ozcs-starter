import type { Room } from "../api";

export function RoomList({ rooms }: { rooms: Room[] }) {
  return (
    <ul className="rooms">
      {rooms.map((room) => (
        <li key={room.id}>
          <strong>{room.name}</strong>
          <span>
            {room.capacity} plaatsen, {room.location}
          </span>
        </li>
      ))}
    </ul>
  );
}
