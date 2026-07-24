<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

function respond($status, $message)
{
    http_response_code($status);
    echo json_encode(['message' => $message], JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    respond(405, 'Método não permitido.');
}

// Honeypot: responde como sucesso sem processar o conteúdo do robô.
if (trim((string) ($_POST['website'] ?? '')) !== '') {
    respond(200, 'Solicitação recebida.');
}

if (($_POST['consentimento'] ?? '') !== 'sim') {
    respond(422, 'É necessário aceitar a Política de Privacidade.');
}

function sanitize_field($value, $limit)
{
    $clean = strip_tags(trim((string) $value));
    $clean = preg_replace('/[\r\n\t]+/u', ' ', $clean) ?? '';
    $clean = preg_replace('/\s{2,}/u', ' ', $clean) ?? '';
    return mb_substr($clean, 0, $limit, 'UTF-8');
}

$tipo = sanitize_field($_POST['tipo'] ?? 'contato', 20);
if ($tipo === 'newsletter') {
    $email = filter_var(trim((string) ($_POST['email'] ?? '')), FILTER_VALIDATE_EMAIL);
    if ($email === false) {
        respond(422, 'Informe um e-mail válido.');
    }
    $hostNewsletter = preg_replace('/[^a-z0-9.-]/i', '', (string) ($_SERVER['SERVER_NAME'] ?? 'localhost')) ?: 'localhost';
    $headersNewsletter = implode("\r\n", [
        'From: Therapeutica <therapeutica@clientehostix.com.br>',
        'Reply-To: therapeutica@clientehostix.com.br',
        'Content-Type: text/plain; charset=UTF-8',
        'X-Mailer: PHP/' . PHP_VERSION,
    ]);
    $corpoNewsletter = "E-mail: {$email}\nConsentimento LGPD: sim\nOrigem: newsletter do site";
    if (!mail('contato@therapeutica.com.br', 'Nova inscrição na newsletter', $corpoNewsletter, $headersNewsletter)) {
        respond(503, 'Não foi possível concluir o cadastro neste momento.');
    }
    respond(200, 'Cadastro realizado com sucesso.');
}

$nome = sanitize_field($_POST['nome'] ?? '', 100);
$telefone = sanitize_field($_POST['telefone'] ?? '', 30);
$unidade = sanitize_field($_POST['unidade'] ?? '', 30);
$mensagem = sanitize_field($_POST['mensagem'] ?? '', 500);
$unidadesPermitidas = ['Sinop', 'Lucas do Rio Verde', 'Sorriso Matriz', 'Sorriso Filial'];

if ($nome === '' || $telefone === '' || !in_array($unidade, $unidadesPermitidas, true)) {
    respond(422, 'Revise os campos obrigatórios e tente novamente.');
}

$anexo = null;
if (!isset($_FILES['receita']) || ($_FILES['receita']['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_NO_FILE) {
    respond(422, 'Anexe a receita em PDF ou DOCX para continuar.');
}
if (isset($_FILES['receita']) && ($_FILES['receita']['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
    $arquivo = $_FILES['receita'];
    if (($arquivo['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
        respond(422, 'Não foi possível receber o anexo. Tente novamente.');
    }
    if (($arquivo['size'] ?? 0) > 5 * 1024 * 1024) {
        respond(422, 'O anexo deve ter no máximo 5 MB.');
    }
    $tiposPermitidos = [
        'application/pdf' => 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document' => 'docx',
    ];
    if (!class_exists('finfo')) {
        respond(500, 'A extensão Fileinfo do PHP precisa ser habilitada no servidor.');
    }
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mime = $finfo->file((string) $arquivo['tmp_name']);
    if (!isset($tiposPermitidos[$mime])) {
        respond(422, 'Envie a receita somente em PDF ou DOCX.');
    }
    $anexo = [
        'tmp' => (string) $arquivo['tmp_name'],
        'mime' => $mime,
        'nome' => 'receita.' . $tiposPermitidos[$mime],
    ];
}

// Endereço provisório: substituir somente após validação do cliente.
$destinatario = 'contato@therapeutica.com.br, em@grupoix.com.br';
$assunto = 'Novo contato pelo site Therapeutica';
$corpo = implode("\n", [
    "Nome: {$nome}",
    "Telefone: {$telefone}",
    "Unidade: {$unidade}",
    "Mensagem: {$mensagem}",
    'Consentimento LGPD: sim',
]);

$host = preg_replace('/[^a-z0-9.-]/i', '', (string) ($_SERVER['SERVER_NAME'] ?? 'localhost')) ?: 'localhost';
$headersBase = [
    'From: Therapeutica <therapeutica@clientehostix.com.br>',
    'Reply-To: therapeutica@clientehostix.com.br',
    'MIME-Version: 1.0',
    'X-Mailer: PHP/' . PHP_VERSION,
];
if ($anexo !== null) {
    $boundary = 'therapeutica_' . bin2hex(random_bytes(12));
    $headersBase[] = "Content-Type: multipart/mixed; boundary=\"{$boundary}\"";
    $corpo = implode("\r\n", [
        "--{$boundary}",
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: 8bit',
        '',
        $corpo,
        "--{$boundary}",
        "Content-Type: {$anexo['mime']}; name=\"{$anexo['nome']}\"",
        'Content-Transfer-Encoding: base64',
        "Content-Disposition: attachment; filename=\"{$anexo['nome']}\"",
        '',
        chunk_split(base64_encode((string) file_get_contents($anexo['tmp']))),
        "--{$boundary}--",
    ]);
} else {
    $headersBase[] = 'Content-Type: text/plain; charset=UTF-8';
}
$headers = implode("\r\n", $headersBase);

if (!function_exists('mail')) {
    respond(500, 'A função mail do PHP não está habilitada nesta hospedagem.');
}

if (!mail($destinatario, $assunto, $corpo, $headers)) {
    respond(503, 'Não foi possível enviar neste momento. Tente novamente mais tarde.');
}

respond(200, 'Recebemos sua solicitação. A equipe retornará em breve.');
