import type { User } from "../api";

interface Props {
  users: User[];
  selected: User | null;
  onPick: (user: User | null) => void;
}

// Dev-login: kies een testgebruiker. In productie komt hier de Microsoft-aanmelding voor in de plaats.
export function UserPicker({ users, selected, onPick }: Props) {
  return (
    <label className="picker">
      Testgebruiker
      <select
        value={selected?.id ?? ""}
        onChange={(e) => onPick(users.find((u) => u.id === Number(e.target.value)) ?? null)}
      >
        <option value="">Kies een gebruiker...</option>
        {users.map((u) => (
          <option key={u.id} value={u.id}>
            {u.display_name} ({u.school_name})
          </option>
        ))}
      </select>
    </label>
  );
}
