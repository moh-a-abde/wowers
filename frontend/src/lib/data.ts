import { useEffect, useState } from "react";
import type { National, PlantCollection, PlantDetail, Portfolio } from "./types";

const BASE = `${import.meta.env.BASE_URL}data`;

async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}/${path}`);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json() as Promise<T>;
}

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let alive = true;
    setData(null);
    setError(null);
    fn()
      .then((d) => alive && setData(d))
      .catch((e) => alive && setError(String(e)));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return { data, error };
}

export const fetchNational = () => getJSON<National>("national.json");
export const fetchPlants = () => getJSON<PlantCollection>("plants.geojson");
export const fetchPortfolio = (state: string) => getJSON<Portfolio>(`portfolio/${state}.json`);
export const fetchPlant = (id: string) => getJSON<PlantDetail>(`plants/${id}.json`);
