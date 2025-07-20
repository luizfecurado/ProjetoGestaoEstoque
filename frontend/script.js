// Configuração da API
const API_BASE_URL = '/api';

// Variáveis globais
let produtos = [];
let pedidos = [];
let itemCounter = 1;

// Funções de navegação
function showSection(sectionName) {
    // Esconder todas as seções
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('produtos-section').style.display = 'none';
    document.getElementById('pedidos-section').style.display = 'none';
    document.getElementById('estoque-section').style.display = 'none';
    
    // Mostrar a seção selecionada
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Atualizar navegação ativa
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    event.target.classList.add('active');
    
    // Carregar dados da seção
    switch(sectionName) {
        case 'dashboard':
            carregarDashboard();
            break;
        case 'produtos':
            carregarProdutos();
            break;
        case 'pedidos':
            carregarPedidos();
            break;
        case 'estoque':
            carregarEstoque();
            break;
    }
}

// Funções da API
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE_URL + endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Dashboard
async function carregarDashboard() {
    try {
        const [produtosData, pedidosData] = await Promise.all([
            apiRequest('/produtos/'),
            apiRequest('/pedidos/')
        ]);
        
        produtos = produtosData;
        pedidos = pedidosData;
        
        // Atualizar estatísticas
        document.getElementById('total-produtos').textContent = produtos.length;
        document.getElementById('total-pedidos').textContent = pedidos.length;
        
        const produtosBaixoEstoque = produtos.filter(p => p.quantidade_estoque < 10).length;
        document.getElementById('produtos-baixo-estoque').textContent = produtosBaixoEstoque;
        
        const valorTotalEstoque = produtos.reduce((total, p) => total + (p.preco * p.quantidade_estoque), 0);
        document.getElementById('valor-total-estoque').textContent = `R$ ${valorTotalEstoque.toFixed(2)}`;
        
        // Listar produtos em baixo estoque
        const baixoEstoqueList = document.getElementById('baixo-estoque-list');
        const produtosBaixo = produtos.filter(p => p.quantidade_estoque < 10);
        baixoEstoqueList.innerHTML = produtosBaixo.length > 0 
            ? produtosBaixo.map(p => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>${p.nome}</span>
                    <span class="badge bg-warning">${p.quantidade_estoque} unidades</span>
                </div>
            `).join('')
            : '<p class="text-muted">Nenhum produto em baixo estoque</p>';
        
        // Listar últimos pedidos
        const ultimosPedidosList = document.getElementById('ultimos-pedidos-list');
        const ultimosPedidos = pedidos.slice(-5).reverse();
        ultimosPedidosList.innerHTML = ultimosPedidos.length > 0
            ? ultimosPedidos.map(p => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${p.cliente}</strong><br>
                        <small class="text-muted">${new Date(p.dataPedido).toLocaleDateString()}</small>
                    </div>
                    <span class="badge bg-success">R$ ${p.valorTotalPedido.toFixed(2)}</span>
                </div>
            `).join('')
            : '<p class="text-muted">Nenhum pedido encontrado</p>';
            
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        alert('Erro ao carregar dados do dashboard');
    }
}

// Produtos
async function carregarProdutos() {
    try {
        produtos = await apiRequest('/produtos/');
        const tbody = document.getElementById('produtos-table');
        
        tbody.innerHTML = produtos.map(produto => `
            <tr>
                <td>${produto.id}</td>
                <td>${produto.nome}</td>
                <td>${produto.descricao || '-'}</td>
                <td>R$ ${produto.preco.toFixed(2)}</td>
                <td>${produto.quantidade_estoque}</td>
                <td>
                    <span class="badge ${produto.quantidade_estoque > 10 ? 'bg-success' : 'bg-warning'} status-badge">
                        ${produto.quantidade_estoque > 10 ? 'Em Estoque' : 'Baixo Estoque'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarProduto(${produto.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="excluirProduto(${produto.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        alert('Erro ao carregar produtos');
    }
}

function showProdutoModal(produtoId = null) {
    const modal = new bootstrap.Modal(document.getElementById('produtoModal'));
    const title = document.getElementById('produtoModalTitle');
    const form = document.getElementById('produtoForm');
    
    if (produtoId) {
        const produto = produtos.find(p => p.id === produtoId);
        title.textContent = 'Editar Produto';
        document.getElementById('produtoNome').value = produto.nome;
        document.getElementById('produtoDescricao').value = produto.descricao || '';
        document.getElementById('produtoPreco').value = produto.preco;
        document.getElementById('produtoEstoque').value = produto.quantidade_estoque;
        form.dataset.produtoId = produtoId;
    } else {
        title.textContent = 'Novo Produto';
        form.reset();
        delete form.dataset.produtoId;
    }
    
    modal.show();
}

async function salvarProduto() {
    const form = document.getElementById('produtoForm');
    const produtoId = form.dataset.produtoId;
    
    const produtoData = {
        nome: document.getElementById('produtoNome').value,
        descricao: document.getElementById('produtoDescricao').value,
        preco: parseFloat(document.getElementById('produtoPreco').value),
        quantidade_estoque: parseInt(document.getElementById('produtoEstoque').value)
    };
    
    try {
        if (produtoId) {
            await apiRequest(`/produtos/${produtoId}`, {
                method: 'PUT',
                body: JSON.stringify(produtoData)
            });
        } else {
            await apiRequest('/produtos/', {
                method: 'POST',
                body: JSON.stringify(produtoData)
            });
        }
        
        bootstrap.Modal.getInstance(document.getElementById('produtoModal')).hide();
        carregarProdutos();
        carregarDashboard();
        alert(produtoId ? 'Produto atualizado com sucesso!' : 'Produto criado com sucesso!');
        
    } catch (error) {
        console.error('Erro ao salvar produto:', error);
        alert('Erro ao salvar produto');
    }
}

async function excluirProduto(produtoId) {
    if (!confirm('Tem certeza que deseja excluir este produto?')) return;
    
    try {
        await apiRequest(`/produtos/${produtoId}`, { method: 'DELETE' });
        carregarProdutos();
        carregarDashboard();
        alert('Produto excluído com sucesso!');
    } catch (error) {
        console.error('Erro ao excluir produto:', error);
        alert('Erro ao excluir produto');
    }
}

function editarProduto(produtoId) {
    showProdutoModal(produtoId);
}

// Pedidos
async function carregarPedidos() {
    try {
        pedidos = await apiRequest('/pedidos/');
        const tbody = document.getElementById('pedidos-table');
        
        tbody.innerHTML = pedidos.map(pedido => `
            <tr>
                <td>${pedido.id}</td>
                <td>${pedido.cliente}</td>
                <td>R$ ${pedido.valorTotalPedido.toFixed(2)}</td>
                <td>${new Date(pedido.dataPedido).toLocaleDateString()}</td>
                <td>${pedido.itens.length} itens</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="verPedido(${pedido.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="excluirPedido(${pedido.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Erro ao carregar pedidos:', error);
        alert('Erro ao carregar pedidos');
    }
}

function showPedidoModal() {
    const modal = new bootstrap.Modal(document.getElementById('pedidoModal'));
    carregarProdutosParaSelect();
    modal.show();
}

function carregarProdutosParaSelect() {
    const selects = document.querySelectorAll('[id^="itemProduto"]');
    selects.forEach(select => {
        select.innerHTML = '<option value="">Selecione um produto</option>' +
            produtos.map(p => `<option value="${p.id}" data-preco="${p.preco}">${p.nome} - R$ ${p.preco.toFixed(2)}</option>`).join('');
    });
}

function adicionarItem() {
    itemCounter++;
    const itemHtml = `
        <div class="row mb-2" id="item${itemCounter}">
            <div class="col-md-4">
                <select class="form-select" id="itemProduto${itemCounter}" onchange="atualizarPreco(${itemCounter})">
                    <option value="">Selecione um produto</option>
                    ${produtos.map(p => `<option value="${p.id}" data-preco="${p.preco}">${p.nome} - R$ ${p.preco.toFixed(2)}</option>`).join('')}
                </select>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" id="itemQuantidade${itemCounter}" placeholder="Qtd" min="1" onchange="calcularItem(${itemCounter})">
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" id="itemPreco${itemCounter}" placeholder="Preço" readonly>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" id="itemTotal${itemCounter}" placeholder="Total" readonly>
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-danger btn-sm" onclick="removerItem(${itemCounter})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    document.getElementById('pedidoItens').insertAdjacentHTML('beforeend', itemHtml);
}

function removerItem(itemId) {
    const item = document.getElementById(`item${itemId}`);
    if (item) {
        item.remove();
        calcularTotalPedido();
    }
}

function atualizarPreco(itemId) {
    const select = document.getElementById(`itemProduto${itemId}`);
    const precoInput = document.getElementById(`itemPreco${itemId}`);
    const quantidadeInput = document.getElementById(`itemQuantidade${itemId}`);
    
    if (select.value) {
        const option = select.options[select.selectedIndex];
        const preco = parseFloat(option.dataset.preco);
        precoInput.value = preco.toFixed(2);
        
        if (quantidadeInput.value) {
            calcularItem(itemId);
        }
    } else {
        precoInput.value = '';
        document.getElementById(`itemTotal${itemId}`).value = '';
    }
}

function calcularItem(itemId) {
    const preco = parseFloat(document.getElementById(`itemPreco${itemId}`).value) || 0;
    const quantidade = parseInt(document.getElementById(`itemQuantidade${itemId}`).value) || 0;
    const total = preco * quantidade;
    
    document.getElementById(`itemTotal${itemId}`).value = total.toFixed(2);
    calcularTotalPedido();
}

function calcularTotalPedido() {
    let total = 0;
    const items = document.querySelectorAll('[id^="itemTotal"]');
    
    items.forEach(item => {
        if (item.value) {
            total += parseFloat(item.value);
        }
    });
    
    document.getElementById('pedidoTotal').textContent = total.toFixed(2);
}

async function salvarPedido() {
    const cliente = document.getElementById('pedidoCliente').value;
    const items = [];
    
    // Coletar itens do pedido
    const itemRows = document.querySelectorAll('[id^="item"]');
    for (let i = 1; i <= itemCounter; i++) {
        const produtoId = document.getElementById(`itemProduto${i}`);
        const quantidade = document.getElementById(`itemQuantidade${i}`);
        
        if (produtoId && produtoId.value && quantidade && quantidade.value) {
            items.push({
                produtoId: parseInt(produtoId.value),
                quantidade: parseInt(quantidade.value)
            });
        }
    }
    
    if (!cliente || items.length === 0) {
        alert('Preencha o cliente e pelo menos um item');
        return;
    }
    
    const pedidoData = {
        cliente: cliente,
        itens: items
    };
    
    try {
        await apiRequest('/pedidos/', {
            method: 'POST',
            body: JSON.stringify(pedidoData)
        });
        
        bootstrap.Modal.getInstance(document.getElementById('pedidoModal')).hide();
        carregarPedidos();
        carregarDashboard();
        alert('Pedido criado com sucesso!');
        
        // Resetar formulário
        document.getElementById('pedidoForm').reset();
        document.getElementById('pedidoItens').innerHTML = `
            <div class="row mb-2">
                <div class="col-md-4">
                    <select class="form-select" id="itemProduto1" onchange="atualizarPreco(1)">
                        <option value="">Selecione um produto</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <input type="number" class="form-control" id="itemQuantidade1" placeholder="Qtd" min="1" onchange="calcularItem(1)">
                </div>
                <div class="col-md-2">
                    <input type="number" class="form-control" id="itemPreco1" placeholder="Preço" readonly>
                </div>
                <div class="col-md-2">
                    <input type="number" class="form-control" id="itemTotal1" placeholder="Total" readonly>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger btn-sm" onclick="removerItem(1)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        itemCounter = 1;
        carregarProdutosParaSelect();
        
    } catch (error) {
        console.error('Erro ao salvar pedido:', error);
        alert('Erro ao salvar pedido');
    }
}

async function excluirPedido(pedidoId) {
    if (!confirm('Tem certeza que deseja excluir este pedido?')) return;
    
    try {
        await apiRequest(`/pedidos/${pedidoId}`, { method: 'DELETE' });
        carregarPedidos();
        carregarDashboard();
        alert('Pedido excluído com sucesso!');
    } catch (error) {
        console.error('Erro ao excluir pedido:', error);
        alert('Erro ao excluir pedido');
    }
}

function verPedido(pedidoId) {
    const pedido = pedidos.find(p => p.id === pedidoId);
    if (pedido) {
        const itens = pedido.itens.map(item => 
            `${item.nome_produto} - ${item.quantidade}x R$ ${item.preco_unitario.toFixed(2)} = R$ ${item.valor_total_item.toFixed(2)}`
        ).join('\n');
        
        alert(`Pedido #${pedido.id}\nCliente: ${pedido.cliente}\nData: ${new Date(pedido.dataPedido).toLocaleDateString()}\n\nItens:\n${itens}\n\nTotal: R$ ${pedido.valorTotalPedido.toFixed(2)}`);
    }
}

// Estoque
async function carregarEstoque() {
    try {
        produtos = await apiRequest('/produtos/');
        const tbody = document.getElementById('estoque-table');
        
        tbody.innerHTML = produtos.map(produto => {
            const valorTotal = produto.preco * produto.quantidade_estoque;
            const status = produto.quantidade_estoque > 10 ? 'Em Estoque' : 
                          produto.quantidade_estoque > 0 ? 'Baixo Estoque' : 'Sem Estoque';
            const statusClass = produto.quantidade_estoque > 10 ? 'bg-success' : 
                               produto.quantidade_estoque > 0 ? 'bg-warning' : 'bg-danger';
            
            return `
                <tr>
                    <td>${produto.nome}</td>
                    <td>${produto.quantidade_estoque}</td>
                    <td>R$ ${produto.preco.toFixed(2)}</td>
                    <td>R$ ${valorTotal.toFixed(2)}</td>
                    <td>
                        <span class="badge ${statusClass} status-badge">${status}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="ajustarEstoque(${produto.id})">
                            <i class="fas fa-edit"></i> Ajustar
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Erro ao carregar estoque:', error);
        alert('Erro ao carregar estoque');
    }
}

function ajustarEstoque(produtoId) {
    const produto = produtos.find(p => p.id === produtoId);
    const novaQuantidade = prompt(`Ajustar estoque de "${produto.nome}"\nQuantidade atual: ${produto.quantidade_estoque}\nNova quantidade:`, produto.quantidade_estoque);
    
    if (novaQuantidade !== null && !isNaN(novaQuantidade)) {
        const quantidade = parseInt(novaQuantidade);
        if (quantidade >= 0) {
            atualizarEstoqueProduto(produtoId, quantidade);
        } else {
            alert('A quantidade deve ser maior ou igual a zero');
        }
    }
}

async function atualizarEstoqueProduto(produtoId, novaQuantidade) {
    try {
        const produto = produtos.find(p => p.id === produtoId);
        await apiRequest(`/produtos/${produtoId}`, {
            method: 'PUT',
            body: JSON.stringify({
                nome: produto.nome,
                descricao: produto.descricao,
                preco: produto.preco,
                quantidade_estoque: novaQuantidade
            })
        });
        
        carregarEstoque();
        carregarDashboard();
        alert('Estoque atualizado com sucesso!');
    } catch (error) {
        console.error('Erro ao atualizar estoque:', error);
        alert('Erro ao atualizar estoque');
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarDashboard();
}); 