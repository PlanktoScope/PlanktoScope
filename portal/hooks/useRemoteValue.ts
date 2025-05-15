import { useEffect, useState } from "react";
import fetch from "@/fetch";

export default function useRemoteValue(
  url: string,
  default_value: string = ""
): [string, (value: string) => Promise<Response>] {
  const [value, setValue] = useState(default_value);

  useEffect(() => {
    async function fetchValue() {
      const res = await fetch(url);
      const body = await res.json();
      setValue(body.value);
    }

    fetchValue().catch(console.error);
  });

  async function submitValue(value: string) {
    return fetch(url, {
      method: "POST",
      body: JSON.stringify({ value }),
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  return [value, submitValue];
}
