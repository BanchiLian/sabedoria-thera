<?php
/**
 * enviar.php — Disparo do formulário "Envie sua Receita" (SoniFarma)
 *
 * Segurança/LGPD:
 *  - Honeypot: se o campo oculto "website" vier preenchido, é bot → descarta.
 *  - Consentimento: sem o checkbox marcado, não processa (LGPD).
 *  - Sanitização de todos os campos antes do e-mail.
 *
 * CONFIGURAR ANTES DE SUBIR: o e-mail de destino em $PARA.
 */

header('Content-Type: application/json; charset=utf-8');

$PARA    = 'contato@sonifarma.com.br';           // <-- AJUSTAR: e-mail que recebe os leads
$ASSUNTO = '[LP SoniFarma] Nova receita recebida';
$DOMINIO = 'sonifarma.com.br';

// só POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'erro' => 'metodo']);
    exit;
}

// honeypot: bots preenchem tudo — humano nunca vê esse campo
if (!empty($_POST['website'])) {
    // responde ok para o bot não insistir, mas não faz nada
    echo json_encode(['ok' => true]);
    exit;
}

// consentimento LGPD obrigatório
if (($_POST['consentimento'] ?? '') !== 'sim') {
    http_response_code(422);
    echo json_encode(['ok' => false, 'erro' => 'consentimento']);
    exit;
}

function campo(string $nome, int $max = 500): string
{
    $v = trim((string)($_POST[$nome] ?? ''));
    $v = strip_tags($v);
    $v = str_replace(["\r", "\n"], ' ', $v);   // evita header injection
    return mb_substr($v, 0, $max);
}

$nome     = campo('nome', 120);
$telefone = campo('telefone', 40);
$email    = campo('email', 160);
$mensagem = mb_substr(strip_tags(trim((string)($_POST['mensagem'] ?? ''))), 0, 2000);

if ($nome === '' || $telefone === '') {
    http_response_code(422);
    echo json_encode(['ok' => false, 'erro' => 'campos']);
    exit;
}
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $email = '';
}

$corpo = "Nova receita enviada pela landing page:\n\n"
       . "Nome:     {$nome}\n"
       . "Telefone: {$telefone}\n"
       . "Email:    " . ($email ?: 'Não informado') . "\n"
       . "Mensagem: " . ($mensagem ?: 'Não informada') . "\n\n"
       . "Consentimento LGPD: SIM (checkbox marcado no envio)\n"
       . "Data: " . date('d/m/Y H:i:s') . "\n"
       . "IP:   " . ($_SERVER['REMOTE_ADDR'] ?? '-') . "\n";

$headers = "From: landing@{$DOMINIO}\r\n"
         . ($email !== '' ? "Reply-To: {$email}\r\n" : '')
         . "X-Mailer: PHP/" . phpversion();

$enviado = mail($PARA, $ASSUNTO, $corpo, $headers);

echo json_encode(['ok' => (bool)$enviado]);
