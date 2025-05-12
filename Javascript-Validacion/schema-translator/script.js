document.addEventListener('DOMContentLoaded', () => {
    const schemaInput = document.getElementById('schema-input');
    const generateTreeButton = document.getElementById('generate-tree');
    const schemaOutput = document.getElementById('schema-output');
    const treeContainer = document.getElementById('tree');
  
    // Función para procesar las definiciones y generar el árbol
    function generateTree(definitions) {
      const lines = definitions.split('\n').map(line => line.trim()).filter(line => line.length > 0);
  
      const root = { name: 'Programa', children: [] };
  
      lines.forEach(line => {
        const tokens = line.split(/\s+/);
        const type = tokens[0];
        const name = tokens[1];
        const rules = tokens.slice(2);
  
        const node = { name, children: [] };
        node.children.push({ name: type });
  
        rules.forEach(rule => {
          node.children.push({ name: rule });
        });
  
        root.children.push(node);
      });
  
      return root;
    }
  
    // Función para renderizar el árbol con D3.js
    function renderTree(treeData) {
      // Limpia el contenedor del árbol
      treeContainer.innerHTML = '';
  
      const width = treeContainer.offsetWidth;
      const height = 500;
  
      const svg = d3.select(treeContainer)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
  
      const g = svg.append('g')
        .attr('transform', 'translate(40,40)');
  
      const treeLayout = d3.tree().size([width - 80, height - 80]);
  
      const root = d3.hierarchy(treeData);
  
      treeLayout(root);
  
      // Enlaces
      g.selectAll('.link')
        .data(root.links())
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', '#ccc');
  
      // Nodos
      const node = g.selectAll('.node')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.x},${d.y})`);
  
      node.append('circle')
        .attr('r', 5)
        .attr('fill', '#69b3a2');
  
      node.append('text')
        .attr('dy', 3)
        .attr('x', d => (d.children ? -10 : 10))
        .style('text-anchor', d => (d.children ? 'end' : 'start'))
        .text(d => d.data.name);
    }
  
    // Evento para generar el árbol al hacer clic en el botón
    generateTreeButton.addEventListener('click', () => {
      const definitions = schemaInput.value;
  
      if (!definitions) {
        alert('Por favor, introduce las definiciones del esquema.');
        return;
      }
  
      const treeData = generateTree(definitions);
  
      // Actualiza el esquema generado
      schemaOutput.textContent = JSON.stringify(treeData, null, 2);
  
      // Renderiza el árbol
      renderTree(treeData);
    });
  });