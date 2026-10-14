// Getypte API-client op één plek. De types spiegelen de Pydantic-schema's in backend/app/schemas.py.
// Wijzigt het contract aan de backendkant, pas dan ook dit bestand aan.

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface Room {
  id: number;
  name: string;
  capacity: number;
  location: string;
}

export interface User {
  id: number;
  display_name: string;
  school_name: string;
}

export interface ReservationCreate {
  room_id: number;
  title: string; // 3 tot 100 tekens
  start: string; // lokale tijd zonder tijdzone, bv. "2026-10-20T09:00"
  end: string; // na start, maximaal 8 uur later
}

export interface Reservation {
  id: number;
  room_id: number;
  room_name: string;
  user_id: number;
  user_display_name: string;
  title: string;
  start: string;
  end: string;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// De dev-login: de gekozen testgebruiker gaat als header mee. In productie vervangt een Entra ID-token dit.
let devUserId: number | null = null;

export function setDevUser(id: number | null): void {
  devUserId = id;
}

function errorMessage(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // Validatiefouten van Pydantic: [{ msg: "Value error, Het einde moet na het begin liggen." }, ...]
    return detail.map((d) => String(d.msg ?? d).replace(/^Value error, /, "")).join(" ");
  }
  return "Er ging iets mis.";
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (devUserId !== null) headers["X-Dev-User"] = String(devUserId);

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorMessage(data.detail));
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const api = {
  devUsers: () => request<User[]>("GET", "/dev/users"),
  rooms: () => request<Room[]>("GET", "/rooms"),
  reservations: (mine: boolean) => request<Reservation[]>("GET", `/reservations?mine=${mine}`),
  createReservation: (data: ReservationCreate) => request<Reservation>("POST", "/reservations", data),
  cancelReservation: (id: number) => request<void>("DELETE", `/reservations/${id}`),
};
