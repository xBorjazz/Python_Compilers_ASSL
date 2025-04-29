// translator.js
const fs = require('fs');
const z = require('zod');

// 1. Lee el archivo de entrada
const input = fs.readFileSync('example.txt', 'utf-8');

// 2. Procesa cada línea
const lines = input.split('\n').map(line => line.trim()).filter(line => line.length > 0);

const schemaDefinition = {};

// 3. Traduce las líneas a objetos Zod
for (const line of lines) {
    const tokens = line.split(/\s+/); // divide por espacios
    const type = tokens[0];
    const name = tokens[1];
    const rules = tokens.slice(2);

    let field;

    switch (type.toLowerCase()) {
        case 'string':
            field = z.string();
            break;
        case 'int':
        case 'integer':
            field = z.number().int();
            break;
        case 'float':
        case 'number':
            field = z.number();
            break;
        case 'boolean':
            field = z.boolean();
            break;
        default:
            throw new Error(`Tipo desconocido: ${type}`);
    }

    // Aplicar reglas adicionales
    for (const rule of rules) {
        if (rule === 'required') {
            // No hacemos nada, será obligatorio de todas formas
        } else if (rule.startsWith('min')) {
            const value = parseInt(rule.replace('min', ''), 10);
            field = field.min(value);
        } else if (rule.startsWith('max')) {
            const value = parseInt(rule.replace('max', ''), 10);
            field = field.max(value);
        } else if (rule.startsWith('pattern=')) {
            const regex = new RegExp(rule.split('=')[1]);
            field = field.regex(regex);
        } else {
            console.warn(`Regla desconocida ignorada: ${rule}`);
        }
    }

    schemaDefinition[name] = field;
}

// 4. Genera el esquema final
const finalSchema = z.object(schemaDefinition);

// 5. Exporta o usa el esquema
console.log('Esquema generado:\n');
console.log(finalSchema);

// 6. Prueba automática: validar un ejemplo
const sampleData = {
    nombre: "Juan",
    edad: 25,
    estudiante: true
};

try {
    const validatedData = finalSchema.parse(sampleData);
    console.log('\nDatos válidos:', validatedData);
} catch (error) {
    console.error('\nErrores de validación:', error.errors);
}
