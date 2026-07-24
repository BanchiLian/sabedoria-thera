<?php
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok' => false]); exit; }
if (!empty($_POST['website'] ?? '')) { echo json_encode(['ok' => true]); exit; }
if (($_POST['consentimento'] ?? '') !== '1') { http_response_code(422); echo json_encode(['ok' => false, 'erro' => 'Consentimento obrigatório.']); exit; }
function limpar($valor) { return trim(strip_tags((string)$valor)); }
$nome = limpar($_POST['nome'] ?? '');
$telefone = preg_replace('/[^0-9()+\-\s]/', '', limpar($_POST['telefone'] ?? ''));
$cidade = limpar($_POST['cidade'] ?? '');
$bairro = limpar($_POST['bairro'] ?? '');
$plano = limpar($_POST['plano'] ?? 'Não informado');
if ($nome === '' || $telefone === '' || $cidade === '' || $bairro === '') { http_response_code(422); echo json_encode(['ok' => false, 'erro' => 'Campos obrigatórios ausentes.']); exit; }
$destino = 'viafibra@viafibra.com.br';
$assunto = 'Novo contato da landing ViaFibra';
$mensagem = "Nome: {$nome}\nTelefone: {$telefone}\nCidade: {$cidade}\nBairro: {$bairro}\nPlano: {$plano}\nConsentimento LGPD: Sim";
$headers = "From: site@viafibra.com.br\r\nReply-To: viafibra@viafibra.com.br\r\nContent-Type: text/plain; charset=UTF-8";
$enviado = mail($destino, $assunto, $mensagem, $headers);
echo json_encode(['ok' => true, 'email_enviado' => $enviado]);
?>
