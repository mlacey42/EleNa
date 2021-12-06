import { MapContainer, Marker, TileLayer } from 'react-leaflet';
import * as styles from '../style/EleNa.module.css';
import 'leaflet/dist/leaflet.css';
import { useState } from 'react';
import SearchField from './SearchField';
import markerIconPng from 'leaflet/dist/images/marker-icon.png';
import { Icon } from 'leaflet';

const EleNa = () => {
    const lat = 42.3869382;
    const lng = -72.52991477067445;
    // const provider = new OpenStreetMapProvider();
    // const prov = OpenStreetMapProvider();

    const [source, setSource] = useState({});
    const [target, setTarget] = useState({});

    // false = min, true = max
    const [elevationGain, setElevationGain] = useState(false);
    const [extraDistance, setExtraDistance] = useState('');

    const onSearch = async () => {
        const obj = {
            city_state: '',
            start: source,
            end: target,
            mode: elevationGain ? 'max' : 'min',
            extra_distance: extraDistance,
        };
        const res = await fetch('/api/elevation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(obj),
        });

        const data = await res.json();
        console.log(data);
    };

    return (
        <div className={styles.EleNa}>
            <div className={styles.header}>
                <div className={styles.locations}>
                    <div className={styles.field}>
                        FROM
                        <SearchField
                            setLocation={(x, y) => setSource({ x, y })}
                        />
                    </div>
                    <br />
                    <div className={styles.field}>
                        TO
                        <SearchField
                            setLocation={(x, y) => setTarget({ x, y })}
                        />
                    </div>
                </div>
                <div className={styles.options}>
                    <div className={styles.field}>
                        ELEVATION GAIN
                        <div>
                            <button
                                disabled={!elevationGain}
                                className={styles.margin_right_small}
                                onClick={() => setElevationGain(false)}
                            >
                                MIN
                            </button>
                            <button
                                disabled={elevationGain}
                                onClick={() => setElevationGain(true)}
                            >
                                MAX
                            </button>
                        </div>
                    </div>
                    <br />
                    <div className={styles.field}>
                        EXTRA DISTANCE
                        <div>
                            <input
                                type="text"
                                className={styles.distance_input}
                                value={extraDistance}
                                onChange={(e) =>
                                    setExtraDistance(e.target.value)
                                }
                            />
                            %
                        </div>
                    </div>
                </div>
                <div className={styles.run}>
                    <button onClick={onSearch}>SEARCH</button>
                </div>
            </div>
            <div className={styles.body}>
                <MapContainer
                    center={[lat, lng]}
                    zoom={13}
                    className={styles.map_container}
                >
                    <TileLayer
                        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {Object.keys(source).length !== 0 &&
                        source.x !== undefined &&
                        source.y !== undefined && (
                            <Marker
                                position={[source.y, source.x]}
                                icon={
                                    new Icon({
                                        iconUrl: markerIconPng,
                                        iconSize: [25, 41],
                                        iconAnchor: [12, 41],
                                    })
                                }
                            />
                        )}
                    {Object.keys(target).length !== 0 &&
                        target.x !== undefined &&
                        target.y !== undefined && (
                            <Marker
                                position={[target.y, target.x]}
                                icon={
                                    new Icon({
                                        iconUrl: markerIconPng,
                                        iconSize: [25, 41],
                                        iconAnchor: [12, 41],
                                    })
                                }
                            />
                        )}
                </MapContainer>
            </div>
        </div>
    );
};

export default EleNa;
