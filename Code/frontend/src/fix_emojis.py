#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# Lire le fichier
with open('App.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver et remplacer la section problématique
# Chercher depuis plant-right jusqu'à la fin des arbres
pattern = r'(<div className="plant-right">🌱</div>\s*<div className="flowers">.*?</div>\s*{/\* Forêt dense.*?\*/}\s*)(<div style={{.*?fontSize: \'33px\' }}>🌲</div>\s*<div style={{.*?fontSize: \'30px\' }}>🌳</div>\s*)(<div style={{.*?left: \'18%\'.*?</div>\s*)*(<div style={{.*?left: \'95%\'.*?</div>)'

# Nouveau contenu avec 16 arbres valides
replacement = '''          {/* Forêt dense - 16 arbres répartis sur toute la largeur */}
          <div style={{ position: 'absolute', bottom: '5px', left: '5%', fontSize: '33px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '12%', fontSize: '30px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '18%', fontSize: '35px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '24%', fontSize: '32px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '30%', fontSize: '34px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '36%', fontSize: '31px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '42%', fontSize: '33px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '48%', fontSize: '30px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '54%', fontSize: '35px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '60%', fontSize: '32px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '66%', fontSize: '34px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '72%', fontSize: '31px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '78%', fontSize: '33px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '84%', fontSize: '32px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '90%', fontSize: '30px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '95%', fontSize: '34px' }}>🌲</div>'''

# Approche plus simple : trouver les lignes spécifiques
lines = content.split('\n')
new_lines = []
skip_mode = False
trees_added = False

for i, line in enumerate(lines):
    # Détecter le début de la section à supprimer
    if 'plant-right' in line and '🌱' in line:
        skip_mode = True
        continue
    
    # Détecter la fin (après le dernier arbre à 95%)
    if skip_mode and "left: '95%" in line and '</div>' in line:
        # Ajouter les nouveaux arbres
        new_lines.append(replacement)
        trees_added = True
        skip_mode = False
        continue
    
    # Sauter les lignes en mode skip
    if skip_mode:
        continue
    
    new_lines.append(line)

# Écrire le résultat
with open('App.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✅ Fleurs supprimées et arbres corrompus remplacés avec succès!")
print(f"✅ {16} arbres valides ajoutés (🌲 🌳 🌴)")
