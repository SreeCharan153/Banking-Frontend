export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined"
    ? window.location.origin.replace(":3000", ":8000") // dev mode
    : "http://localhost:8000");
