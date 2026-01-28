# amod

Prototype d'IA heuristique pour simuler des résultats socio-économiques après différents événements
(temps, épidémie, facteurs sociaux, stabilité politique, conflit externe, etc.).

## Démarrage rapide

```bash
python -m amod.cli --years 10 --epidemic 0.7 --political 0.5 --fear-factor 0.6 --output summary
```

Pour intégrer la volatilité des marchés (VIX) et le Doomsday Clock :

```bash
python -m amod.cli --years 10 --fetch-market-data --fear-factor 0.4 --output summary
```

### Exemple de sortie

```json
{
  "gdp_index": 0.41,
  "unemployment_rate": 0.49,
  "inequality_index": 0.55,
  "health_index": 0.33,
  "social_cohesion": 0.38,
  "political_stability": 0.42,
  "institutional_trust": 0.37
}
```

## Principes du modèle

- Les variables sont normalisées entre 0 et 1.
- Le modèle est heuristique et sert à explorer des scénarios plutôt qu'à prédire la réalité.
- Les facteurs d'événements s'appliquent sur l'horizon défini et influencent progressivement
  les indicateurs macro-sociaux.
- Le **fear factor** réduit la propension à investir et amplifie certains effets négatifs.
- L'option `--fetch-market-data` récupère le VIX et le Doomsday Clock pour estimer la panique
  des marchés, combinée avec le fear factor fourni.

## Structure

- `amod/simulation.py` : cœur du modèle et des formules.
- `amod/cli.py` : CLI pour lancer des simulations et obtenir un résumé ou la timeline complète.
- `amod/market_data.py` : récupération du VIX et du Doomsday Clock, calcul d'un indice de panique.

## Tester rapidement

Simulation locale (sans données marché) :

```bash
python -m amod.cli --years 1 --output summary
```

Simulation avec récupération du VIX et du Doomsday Clock :

```bash
python -m amod.cli --years 1 --fetch-market-data --output summary
```
