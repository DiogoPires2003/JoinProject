const { test, expect } = require('@playwright/test');

test('registro exitoso de nuevo usuario', async ({ page }) => {
  await page.goto('http://localhost:8000/');
  await page.getByRole('button', { name: 'Toggle navigation' }).click();
  await page.getByRole('link', { name: 'Acceder/Registrar-se' }).click();
  await page.getByRole('link', { name: 'Registrarse' }).click();
  await page.getByRole('textbox', { name: 'Nombre' }).click();
  await page.getByRole('textbox', { name: 'Nombre' }).fill('test');
  await page.getByRole('textbox', { name: 'Apellido' }).click();
  await page.getByRole('textbox', { name: 'Apellido' }).fill('test');
  await page.getByRole('textbox', { name: 'DNI/NIE' }).click();
  await page.getByRole('textbox', { name: 'DNI/NIE' }).fill('12345678R');
  await page.getByRole('textbox', { name: 'Correo electrónico' }).click();
  await page.getByRole('textbox', { name: 'Correo electrónico' }).fill('test@test.com');
  await page.getByRole('textbox', { name: 'Número de teléfono' }).click();
  await page.getByRole('textbox', { name: 'Número de teléfono' }).fill('123123123');
  await page.getByRole('textbox', { name: 'Contraseña', exact: true }).click();
  await page.getByRole('textbox', { name: 'Contraseña', exact: true }).fill('123123123');
  await page.getByRole('textbox', { name: 'Confirmar contraseña' }).click();
  await page.getByRole('textbox', { name: 'Confirmar contraseña' }).fill('123123123');
  await page.getByRole('button', { name: 'Registrarse' }).click();
  await page.goto('http://localhost:8000/login/');
});