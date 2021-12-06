import { useEffect, useState } from 'react';
import * as styles from '../style/SearchField.module.css';
import { OpenStreetMapProvider } from 'leaflet-geosearch';

const Suggestion = ({ suggestion, onClick }) => {
    return (
        <div className={styles.tag} onClick={onClick}>
            {suggestion.label}
            <div className={styles.line} />
        </div>
    );
};

function SearchField({ setLocation, clearRoute }) {
    const [suggestions, setSuggestions] = useState([]);
    const [focus, setFocus] = useState(false);
    const [choose, setChoose] = useState(false);
    const [value, setValue] = useState('');
    useEffect(() => {
        const exec = setTimeout(async () => {
            clearRoute();
            const query = value.trim();
            if (query) {
                const provider = new OpenStreetMapProvider();
                const results = await provider.search({ query });
                setSuggestions(results);
            } else {
                setLocation([]);
                setSuggestions([]);
            }
        }, 500);
        return () => clearTimeout(exec);
    }, [value, clearRoute, setLocation]);
    return (
        <div className={styles.container}>
            <input
                type="text"
                placeholder="Search for a location"
                onChange={(e) => {
                    setValue(e.target.value);
                    setChoose(false);
                }}
                value={value}
                onFocus={() => setFocus(true)}
                onBlur={() => {
                    setTimeout(() => {
                        if (!choose && suggestions.length !== 0) {
                            setFocus(false);
                            setValue(suggestions[0].label);
                            setLocation(suggestions[0].x, suggestions[0].y);
                        }
                    }, 100);
                }}
            />
            <div className={styles.suggestion}>
                {focus &&
                    suggestions.map((suggestion) => (
                        <Suggestion
                            key={suggestion.x}
                            suggestion={suggestion}
                            onClick={() => {
                                setValue(suggestion.label);
                                setLocation(suggestion.x, suggestion.y);
                                setChoose(true);
                            }}
                        />
                    ))}
            </div>
        </div>
    );
}

export default SearchField;
