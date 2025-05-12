import { TreeNode } from './tree.js';
import fs from 'fs';

// 1. Lee el archivo de entrada
const input = fs.readFileSync('./schema-translator/example.txt', 'utf-8');

// 2. Procesa cada línea
const lines = input.split('\n').map(line => line.trim()).filter(line => line.length > 0);

const schemaDefinition = {};
const root = new TreeNode('Programa'); // Nodo raíz del árbol

// 3. Traduce las líneas a nodos del árbol
lines.forEach(line => {
  const tokens = line.split(/\s+/);
  const type = tokens[0];
  const name = tokens[1];
  const rules = tokens.slice(2);

  const node = new TreeNode(name);
  node.addChild(new TreeNode(type));

  rules.forEach(rule => {
    node.addChild(new TreeNode(rule));
  });

  root.addChild(node);
});

// 4. Exporta el esquema y el árbol
const output = {
  schema: schemaDefinition,
  tree: root
};

fs.writeFileSync('./schema-translator/output.json', JSON.stringify(output, null, 2), 'utf-8');
console.log('Datos exportados a output.json');