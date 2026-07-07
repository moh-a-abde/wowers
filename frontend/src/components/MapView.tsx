import { useEffect, useMemo, useRef, useState } from "react";
import Map, { Layer, Marker, Popup, Source } from "react-map-gl/maplibre";
import type { MapRef } from "react-map-gl/maplibre";
import type { MapLayerMouseEvent, StyleSpecification } from "maplibre-gl";
import { useNavigate } from "react-router-dom";
import type { MapProps, PlantCollection } from "../lib/types";
import { BAND_COLOR } from "../lib/colors";
import { mwh, usd, years } from "../lib/format";

const SATELLITE: StyleSpecification = {
  version: 8,
  sources: {
    esri: {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      attribution: "Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics",
    },
  },
  layers: [{ id: "esri", type: "raster", source: "esri" }],
};

const NATIONAL_VIEW = { longitude: -96, latitude: 38.5, zoom: 3.6 };

export type LngLatBounds = [[number, number], [number, number]]; // [[w, s], [e, n]]

export default function MapView({
  data,
  bounds,
}: {
  data: PlantCollection;
  /** When set, the map eases to fit these bounds; when cleared, back to national view. */
  bounds?: LngLatBounds | null;
}) {
  const nav = useNavigate();
  const mapRef = useRef<MapRef>(null);
  const [loaded, setLoaded] = useState(false);
  const [hover, setHover] = useState<{ lng: number; lat: number; p: MapProps } | null>(null);

  // Runs once the map instance exists (onLoad) and again on bounds changes,
  // so a deep-linked ?state=XX zooms correctly on first paint.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded) return;
    if (bounds) {
      map.fitBounds(bounds, { padding: 60, maxZoom: 9, duration: 900 });
    } else {
      map.easeTo({ center: [NATIONAL_VIEW.longitude, NATIONAL_VIEW.latitude], zoom: NATIONAL_VIEW.zoom, duration: 900 });
    }
  }, [bounds, loaded]);

  const circleColor = useMemo(
    () =>
      [
        "match",
        ["get", "band"],
        "high", BAND_COLOR.high,
        "moderate", BAND_COLOR.moderate,
        "marginal", BAND_COLOR.marginal,
        BAND_COLOR.nonviable,
      ] as never,
    [],
  );

  const onClick = (e: MapLayerMouseEvent) => {
    const f = e.features?.[0];
    if (f) nav(`/plant/${(f.properties as MapProps).id}`);
  };
  const onMove = (e: MapLayerMouseEvent) => {
    const f = e.features?.[0];
    setHover(f ? { lng: e.lngLat.lng, lat: e.lngLat.lat, p: f.properties as MapProps } : null);
  };

  return (
    <Map
      ref={mapRef}
      initialViewState={NATIONAL_VIEW}
      onLoad={() => setLoaded(true)}
      mapStyle={SATELLITE}
      interactiveLayerIds={["plants"]}
      onClick={onClick}
      onMouseMove={onMove}
      onMouseLeave={() => setHover(null)}
      cursor={hover ? "pointer" : "grab"}
      style={{ width: "100%", height: "100%" }}
    >
      <Source id="plants" type="geojson" data={data}>
        <Layer
          id="plants"
          type="circle"
          paint={{
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, 2.6, 6, 5, 10, 8],
            "circle-color": circleColor,
            "circle-opacity": 0.85,
            "circle-stroke-width": 0.4,
            "circle-stroke-color": "#0a1f44",
          }}
        />
      </Source>
      {hover && (
        <Popup longitude={hover.lng} latitude={hover.lat} closeButton={false} offset={12} anchor="bottom">
          <div style={{ fontSize: 12, minWidth: 150 }}>
            <strong>{hover.p.name}</strong>
            <div className="muted">{hover.p.city}, {hover.p.state}</div>
            <div style={{ marginTop: 4 }}>Energy: {mwh(hover.p.energy_mwh)}</div>
            <div>Payback: {years(hover.p.payback)}</div>
            <div>NPV: {usd(hover.p.npv)} · {hover.p.turbine}</div>
            <div style={{ color: "#2563eb", marginTop: 3 }}>Click for full report →</div>
          </div>
        </Popup>
      )}
    </Map>
  );
}

/** Small single-site locator map for the plant detail page. */
export function MiniMap({ lat, lon }: { lat: number; lon: number }) {
  return (
    <div style={{ height: 220, borderRadius: 8, overflow: "hidden" }}>
      <Map
        initialViewState={{ longitude: lon, latitude: lat, zoom: 13 }}
        mapStyle={SATELLITE}
        style={{ width: "100%", height: "100%" }}
      >
        <Marker longitude={lon} latitude={lat} anchor="center">
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              background: "#2563eb",
              border: "3px solid #fff",
              boxShadow: "0 0 0 2px rgba(37,99,235,.45), 0 2px 6px rgba(0,0,0,.4)",
            }}
          />
        </Marker>
      </Map>
    </div>
  );
}
