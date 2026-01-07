// MF Dashboard JavaScript

// Portfolio Data - Starts empty, load your data via Import
let portfolioData = {
    portfolio_name: "My Portfolio",
    accounts: {}
};

// Chart instances
let allocationChart = null;
let performanceChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    setupEventListeners();
});

// Load dashboard data
function loadDashboard() {
    updateSummaryCards();
    renderHoldingsTable();
    renderAccountsGrid();
    renderCharts();
}

// Update summary cards
function updateSummaryCards() {
    let totalInvested = 0;
    let totalCurrent = 0;

    // Calculate totals
    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        for (let holding of account.holdings) {
            totalInvested += holding.invested;
            totalCurrent += holding.current_value;
        }
    }

    const totalGain = totalCurrent - totalInvested;
    const gainPercentage = totalInvested > 0 ? (totalGain / totalInvested) * 100 : 0;

    // Calculate XIRR (simplified - in production use actual XIRR calculation)
    const xirr = totalInvested > 0 ? calculatePortfolioXIRR() : 0;

    // Update DOM
    document.getElementById('totalInvested').textContent = formatCurrency(totalInvested);
    document.getElementById('currentValue').textContent = formatCurrency(totalCurrent);

    const gainElement = document.getElementById('totalGain');
    gainElement.textContent = formatCurrency(totalGain);

    const percentElement = document.getElementById('gainPercentage');
    percentElement.textContent = formatPercentage(gainPercentage);
    percentElement.className = 'percentage ' + (totalGain >= 0 ? 'positive' : 'negative');

    document.getElementById('xirr').textContent = formatPercentage(xirr);
}

// Render holdings table
function renderHoldingsTable() {
    const tbody = document.getElementById('holdingsTableBody');
    tbody.innerHTML = '';

    let allHoldings = [];

    // Collect all holdings with PAN info
    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        for (let i = 0; i < account.holdings.length; i++) {
            allHoldings.push({ ...account.holdings[i], pan: pan, originalIndex: i });
        }
    }

    // Update PAN filter dropdown
    updatePanFilter();

    // Show message if no holdings
    if (allHoldings.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="10" style="text-align: center; padding: 40px; color: #64748b;">
                <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 16px; display: block;"></i>
                <strong>No Holdings Found</strong><br>
                <small>Click the "Import" button above to import your portfolio data from Excel or CSV</small>
            </td>
        `;
        tbody.appendChild(row);
        return;
    }

    // Render rows
    for (let i = 0; i < allHoldings.length; i++) {
        const holding = allHoldings[i];
        const avgPrice = holding.invested / holding.units;
        const gainLoss = holding.current_value - holding.invested;
        const returnPct = (gainLoss / holding.invested) * 100;

        const row = document.createElement('tr');
        row.setAttribute('data-pan', holding.pan);
        row.setAttribute('data-category', holding.category || '');
        row.innerHTML = `
            <td><strong>${holding.scheme_name}</strong><br><small>${holding.pan}</small></td>
            <td>${holding.folio}</td>
            <td class="text-right">${holding.units.toFixed(3)}</td>
            <td class="text-right">${formatCurrency(avgPrice)}</td>
            <td class="text-right">${formatCurrency(holding.invested)}</td>
            <td class="text-right">${formatCurrency(holding.current_nav)}</td>
            <td class="text-right"><strong>${formatCurrency(holding.current_value)}</strong></td>
            <td class="text-right ${gainLoss >= 0 ? 'text-success' : 'text-danger'}">
                ${formatCurrency(gainLoss)}
            </td>
            <td class="text-right ${returnPct >= 0 ? 'text-success' : 'text-danger'}">
                ${formatPercentage(returnPct)}
            </td>
            <td class="text-center">
                <button class="btn-icon btn-edit" data-pan="${holding.pan}" data-index="${holding.originalIndex}" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon btn-delete" data-pan="${holding.pan}" data-index="${holding.originalIndex}" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

// Render accounts grid
function renderAccountsGrid() {
    const grid = document.getElementById('accountsGrid');
    grid.innerHTML = '';

    const accountCount = Object.keys(portfolioData.accounts).length;

    // Show message if no accounts
    if (accountCount === 0) {
        grid.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #64748b; grid-column: 1 / -1;">
                <i class="fas fa-users" style="font-size: 48px; margin-bottom: 16px; display: block;"></i>
                <strong>No Accounts Found</strong><br>
                <small>Import your portfolio to see account summaries</small>
            </div>
        `;
        return;
    }

    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];

        let invested = 0;
        let currentValue = 0;

        for (let holding of account.holdings) {
            invested += holding.invested;
            currentValue += holding.current_value;
        }

        const gain = currentValue - invested;
        const returnPct = invested > 0 ? (gain / invested) * 100 : 0;

        const card = document.createElement('div');
        card.className = 'account-card';
        card.innerHTML = `
            <h3><i class="fas fa-user-circle"></i> ${account.name}</h3>
            <p><strong>PAN:</strong> ${pan}</p>
            <p><strong>Holdings:</strong> ${account.holdings.length}</p>
            <p><strong>Invested:</strong> ${formatCurrency(invested)}</p>
            <p class="account-value">${formatCurrency(currentValue)}</p>
            <p class="${gain >= 0 ? 'text-success' : 'text-danger'}">
                <strong>${formatCurrency(gain)} (${formatPercentage(returnPct)})</strong>
            </p>
        `;
        grid.appendChild(card);
    }
}

// Render charts
function renderCharts() {
    renderAllocationChart();
    renderPerformanceChart();
}

// Allocation pie chart
function renderAllocationChart() {
    const ctx = document.getElementById('allocationChart').getContext('2d');

    // Destroy existing chart
    if (allocationChart) {
        allocationChart.destroy();
        allocationChart = null;
    }

    // Prepare data
    const labels = [];
    const data = [];
    const colors = [
        '#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
    ];

    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        for (let holding of account.holdings) {
            labels.push(holding.scheme_name.substring(0, 30) + '...');
            data.push(holding.current_value);
        }
    }

    // Don't render chart if no data
    if (data.length === 0) {
        return;
    }

    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = formatCurrency(context.parsed);
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Performance bar chart
function renderPerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');

    // Destroy existing chart
    if (performanceChart) {
        performanceChart.destroy();
        performanceChart = null;
    }

    // Prepare data
    const labels = [];
    const investedData = [];
    const currentData = [];

    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        for (let holding of account.holdings) {
            labels.push(holding.scheme_name.substring(0, 25) + '...');
            investedData.push(holding.invested);
            currentData.push(holding.current_value);
        }
    }

    // Don't render chart if no data
    if (labels.length === 0) {
        return;
    }

    performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Invested',
                    data: investedData,
                    backgroundColor: '#64748b',
                },
                {
                    label: 'Current Value',
                    data: currentData,
                    backgroundColor: '#10b981',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                }
            }
        }
    });
}

// Calculate portfolio XIRR (simplified)
function calculatePortfolioXIRR() {
    // In production, implement actual XIRR calculation
    // For now, return a sample value
    return 12.5;
}

// Format currency
function formatCurrency(amount) {
    return '₹' + amount.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format percentage
function formatPercentage(value) {
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(2) + '%';
}

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', function() {
        this.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';

        // Simulate refresh
        setTimeout(() => {
            loadDashboard();
            this.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        }, 1000);
    });

    // Import button
    document.getElementById('importBtn').addEventListener('click', function() {
        document.getElementById('importModal').style.display = 'block';
    });

    // Export button
    document.getElementById('exportBtn').addEventListener('click', function() {
        document.getElementById('exportModal').style.display = 'block';
    });

    // Modal close buttons
    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('exportModal').style.display = 'none';
    });

    document.querySelector('.close-import').addEventListener('click', function() {
        document.getElementById('importModal').style.display = 'none';
    });

    // Close modal on outside click
    window.addEventListener('click', function(event) {
        const exportModal = document.getElementById('exportModal');
        const importModal = document.getElementById('importModal');

        if (event.target === exportModal) {
            exportModal.style.display = 'none';
        }

        if (event.target === importModal) {
            importModal.style.display = 'none';
        }
    });

    // Export buttons
    document.getElementById('exportExcelBtn').addEventListener('click', function() {
        alert('Excel export functionality - connect to backend API');
        document.getElementById('exportModal').style.display = 'none';
    });

    document.getElementById('exportJsonBtn').addEventListener('click', function() {
        downloadJSON();
        document.getElementById('exportModal').style.display = 'none';
    });

    document.getElementById('exportCsvBtn').addEventListener('click', function() {
        downloadCSV();
        document.getElementById('exportModal').style.display = 'none';
    });

    document.getElementById('exportPdfBtn').addEventListener('click', function() {
        alert('PDF export functionality - connect to backend API');
        document.getElementById('exportModal').style.display = 'none';
    });

    // Import functionality
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    const importStatus = document.getElementById('importStatus');

    // Click to browse files
    fileUploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });

    // Drag and drop
    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileUploadArea.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileUploadArea.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileUploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // Import button handlers
    document.getElementById('importCsvBtn').addEventListener('click', function() {
        fileInput.setAttribute('accept', '.csv');
        fileInput.click();
    });

    document.getElementById('importExcelBtn').addEventListener('click', function() {
        fileInput.setAttribute('accept', '.xlsx,.xls');
        fileInput.click();
    });

    document.getElementById('importJsonBtn').addEventListener('click', function() {
        fileInput.setAttribute('accept', '.json');
        fileInput.click();
    });
}

// Download JSON
function downloadJSON() {
    const dataStr = JSON.stringify(portfolioData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'portfolio_export.json';
    link.click();

    URL.revokeObjectURL(url);
}

// Download CSV
function downloadCSV() {
    // Generate CSV from portfolio data
    let csv = 'PAN,Scheme Name,Folio,Units,Invested,Current NAV,Current Value,Gain/Loss,Return %\n';

    for (let pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        for (let holding of account.holdings) {
            const gainLoss = holding.current_value - holding.invested;
            const returnPct = (gainLoss / holding.invested) * 100;

            csv += `${pan},${holding.scheme_name},${holding.folio},${holding.units},${holding.invested},${holding.current_nav},${holding.current_value},${gainLoss},${returnPct.toFixed(2)}\n`;
        }
    }

    const dataBlob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'portfolio_export.csv';
    link.click();

    URL.revokeObjectURL(url);
}

// Handle file imports
function handleFiles(files) {
    const importStatus = document.getElementById('importStatus');

    if (files.length === 0) {
        return;
    }

    const file = files[0];
    const fileName = file.name.toLowerCase();

    // Get import mode
    const importMode = document.querySelector('input[name="importMode"]:checked').value;

    importStatus.classList.remove('hidden', 'success', 'error');
    importStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing file...';
    importStatus.classList.remove('hidden');

    if (fileName.endsWith('.json')) {
        // Load JSON file
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const importedData = JSON.parse(e.target.result);

                if (importMode === 'merge') {
                    portfolioData = mergePortfolioData(portfolioData, importedData);
                } else {
                    portfolioData = importedData;
                }

                loadDashboard();

                importStatus.classList.add('success');
                const modeText = importMode === 'merge' ? 'merged' : 'imported';
                importStatus.innerHTML = `<i class="fas fa-check-circle"></i> Portfolio ${modeText} successfully!`;

                setTimeout(function() {
                    document.getElementById('importModal').style.display = 'none';
                    importStatus.classList.add('hidden');
                }, 2000);
            } catch (error) {
                importStatus.classList.add('error');
                importStatus.innerHTML = '<i class="fas fa-times-circle"></i> Error: ' + error.message;
            }
        };
        reader.readAsText(file);
    } else if (fileName.endsWith('.csv')) {
        // CSV import (client-side processing)
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const csvData = e.target.result;
                const importedData = parseCSV(csvData);

                if (importedData) {
                    if (importMode === 'merge') {
                        portfolioData = mergePortfolioData(portfolioData, importedData);
                    } else {
                        portfolioData = importedData;
                    }

                    loadDashboard();

                    importStatus.classList.add('success');
                    const modeText = importMode === 'merge' ? 'merged' : 'imported';
                    importStatus.innerHTML = `<i class="fas fa-check-circle"></i> CSV ${modeText} successfully! Total accounts: ` +
                        Object.keys(portfolioData.accounts).length;

                    setTimeout(function() {
                        document.getElementById('importModal').style.display = 'none';
                        importStatus.classList.add('hidden');
                    }, 2000);
                } else {
                    throw new Error('Could not parse CSV file');
                }
            } catch (error) {
                importStatus.classList.add('error');
                importStatus.innerHTML = '<i class="fas fa-times-circle"></i> Error: ' + error.message;
            }
        };
        reader.readAsText(file);
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        // Excel import (client-side using SheetJS)
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });

                // Parse the Excel file
                const importedData = parseExcel(workbook);

                if (importedData) {
                    if (importMode === 'merge') {
                        portfolioData = mergePortfolioData(portfolioData, importedData);
                    } else {
                        portfolioData = importedData;
                    }

                    loadDashboard();

                    importStatus.classList.add('success');
                    const modeText = importMode === 'merge' ? 'merged' : 'imported';
                    importStatus.innerHTML = `<i class="fas fa-check-circle"></i> Excel ${modeText} successfully! Total accounts: ` +
                        Object.keys(portfolioData.accounts).length;

                    setTimeout(function() {
                        document.getElementById('importModal').style.display = 'none';
                        importStatus.classList.add('hidden');
                    }, 2000);
                } else {
                    throw new Error('Could not parse Excel file');
                }
            } catch (error) {
                importStatus.classList.add('error');
                importStatus.innerHTML = '<i class="fas fa-times-circle"></i> Error: ' + error.message;
            }
        };
        reader.readAsArrayBuffer(file);
    } else {
        importStatus.classList.add('error');
        importStatus.innerHTML = '<i class="fas fa-times-circle"></i> Unsupported file format. Please use CSV, Excel, or JSON files.';
    }
}

// Parse Excel workbook and convert to portfolio format
function parseExcel(workbook) {
    // Try to find Holdings sheet
    let sheetName = 'Holdings';

    if (!workbook.SheetNames.includes(sheetName)) {
        // Try first sheet if Holdings not found
        sheetName = workbook.SheetNames[0];

        if (!sheetName) {
            throw new Error('No sheets found in Excel file');
        }
    }

    const worksheet = workbook.Sheets[sheetName];

    // Convert sheet to JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: '' });

    if (jsonData.length === 0) {
        throw new Error('Excel sheet is empty');
    }

    // Check if this has holdings data
    const firstRow = jsonData[0];
    const hasSchemeData = 'Scheme Name' in firstRow || 'Scheme Code' in firstRow;

    if (!hasSchemeData) {
        // Show available columns for debugging
        const availableColumns = Object.keys(firstRow).join(', ');
        console.log('Available columns in Excel:', availableColumns);
        throw new Error('Excel must contain holdings data with "Scheme Name" or "Scheme Code" column. Found columns: ' + availableColumns);
    }

    // Log detected columns for debugging
    console.log('Importing from Excel sheet:', sheetName);
    console.log('Columns found:', Object.keys(firstRow).join(', '));
    console.log('Rows to import:', jsonData.length);

    // Parse holdings data
    const holdings = {};

    for (const row of jsonData) {
        // Extract PAN
        const pan = row['PAN'] || 'IMPORTED';

        // Skip total rows
        if (pan.toUpperCase() === 'TOTAL') {
            continue;
        }

        // Initialize PAN account if needed
        if (!holdings[pan]) {
            holdings[pan] = {
                name: row['Account Name'] || 'Imported Account',
                email: row['Email'] || '',
                holdings: []
            };
        }

        // Helper function to get value from multiple possible column names
        const getColumnValue = (row, possibleNames, fieldName) => {
            // Try exact match first
            for (let name of possibleNames) {
                if (row[name] !== undefined && row[name] !== null && row[name] !== '') {
                    console.log(`✓ Found ${fieldName} in column: "${name}" = ${row[name]}`);
                    return row[name];
                }
            }

            // Try case-insensitive match
            for (let name of possibleNames) {
                const matchingKey = Object.keys(row).find(key =>
                    key.toLowerCase().trim() === name.toLowerCase().trim()
                );
                if (matchingKey && row[matchingKey] !== undefined && row[matchingKey] !== null && row[matchingKey] !== '') {
                    console.log(`✓ Found ${fieldName} in column (case-insensitive): "${matchingKey}" = ${row[matchingKey]}`);
                    return row[matchingKey];
                }
            }

            console.warn(`⚠ ${fieldName} column not found. Looking for one of: ${possibleNames.join(', ')}`);
            console.warn(`   Available columns: ${Object.keys(row).join(', ')}`);
            return '';
        };

        // Extract values with flexible column names
        const units = parseFloat(getColumnValue(row, ['Units', 'Unit', 'Quantity'], 'Units')) || 0;
        const invested = parseFloat(getColumnValue(row, ['Invested Amount', 'Invested', 'Investment', 'Cost', 'Purchase Value', 'Invested Value', 'Total Invested', 'Amount Invested'], 'Invested')) || 0;
        const currentNav = parseFloat(getColumnValue(row, ['Current NAV', 'NAV', 'Latest NAV', 'Current Price', 'Price'], 'Current NAV')) || 0;
        const currentValue = parseFloat(getColumnValue(row, ['Current Value', 'Market Value', 'Value', 'Total Value'], 'Current Value')) || 0;

        // Debug: Log values for each row to help troubleshoot
        console.log('=== Parsed row ===');
        console.log('Scheme Name:', row['Scheme Name']);
        console.log('Units:', units);
        console.log('Invested:', invested);
        console.log('Current NAV:', currentNav);
        console.log('Current Value:', currentValue);
        console.log('================');

        // Create holding object
        const holding = {
            scheme_code: String(row['Scheme Code'] || ''),
            scheme_name: String(row['Scheme Name'] || ''),
            folio: String(row['Folio'] || ''),
            category: String(row['Category'] || ''),
            units: units,
            invested: invested,
            current_nav: currentNav,
            current_value: currentValue,
            nav_date: String(row['NAV Date'] || ''),
            transactions: []
        };

        holdings[pan].holdings.push(holding);
    }

    // Create portfolio structure
    const portfolio = {
        portfolio_name: 'Imported Portfolio - ' + new Date().toLocaleDateString(),
        created_date: new Date().toISOString(),
        accounts: holdings
    };

    return portfolio;
}

// Parse CSV data and convert to portfolio format
function parseCSV(csvData) {
    const lines = csvData.split('\n').filter(line => line.trim() !== '');

    if (lines.length < 2) {
        throw new Error('CSV file is empty or invalid');
    }

    // Parse header
    const headers = lines[0].split(',').map(h => h.trim());

    // Check if this is a holdings CSV
    const isHoldingsCSV = headers.includes('Scheme Name') || headers.includes('Scheme Code');

    if (!isHoldingsCSV) {
        throw new Error('CSV must contain holdings data with "Scheme Name" or "Scheme Code" column');
    }

    // Parse data rows
    const holdings = {};

    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);

        if (values.length !== headers.length) {
            continue; // Skip malformed rows
        }

        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index];
        });

        // Extract PAN
        const pan = row['PAN'] || 'IMPORTED';

        // Skip total rows
        if (pan.toUpperCase() === 'TOTAL') {
            continue;
        }

        // Initialize PAN account if needed
        if (!holdings[pan]) {
            holdings[pan] = {
                name: row['Account Name'] || 'Imported Account',
                email: row['Email'] || '',
                holdings: []
            };
        }

        // Helper function to get value from multiple possible column names
        const getColumnValue = (row, possibleNames, fieldName) => {
            // Try exact match first
            for (let name of possibleNames) {
                if (row[name] !== undefined && row[name] !== null && row[name] !== '') {
                    console.log(`✓ Found ${fieldName} in column: "${name}" = ${row[name]}`);
                    return row[name];
                }
            }

            // Try case-insensitive match
            for (let name of possibleNames) {
                const matchingKey = Object.keys(row).find(key =>
                    key.toLowerCase().trim() === name.toLowerCase().trim()
                );
                if (matchingKey && row[matchingKey] !== undefined && row[matchingKey] !== null && row[matchingKey] !== '') {
                    console.log(`✓ Found ${fieldName} in column (case-insensitive): "${matchingKey}" = ${row[matchingKey]}`);
                    return row[matchingKey];
                }
            }

            console.warn(`⚠ ${fieldName} column not found. Looking for one of: ${possibleNames.join(', ')}`);
            console.warn(`   Available columns: ${Object.keys(row).join(', ')}`);
            return '';
        };

        // Extract values with flexible column names
        const units = parseFloat(getColumnValue(row, ['Units', 'Unit', 'Quantity'], 'Units')) || 0;
        const invested = parseFloat(getColumnValue(row, ['Invested Amount', 'Invested', 'Investment', 'Cost', 'Purchase Value', 'Invested Value', 'Total Invested', 'Amount Invested'], 'Invested')) || 0;
        const currentNav = parseFloat(getColumnValue(row, ['Current NAV', 'NAV', 'Latest NAV', 'Current Price', 'Price'], 'Current NAV')) || 0;
        const currentValue = parseFloat(getColumnValue(row, ['Current Value', 'Market Value', 'Value', 'Total Value'], 'Current Value')) || 0;

        // Create holding object
        const holding = {
            scheme_code: row['Scheme Code'] || '',
            scheme_name: row['Scheme Name'] || '',
            folio: row['Folio'] || '',
            category: row['Category'] || '',
            units: units,
            invested: invested,
            current_nav: currentNav,
            current_value: currentValue,
            nav_date: row['NAV Date'] || '',
            transactions: []
        };

        holdings[pan].holdings.push(holding);
    }

    // Create portfolio structure
    const portfolio = {
        portfolio_name: 'Imported Portfolio - ' + new Date().toLocaleDateString(),
        created_date: new Date().toISOString(),
        accounts: holdings
    };

    return portfolio;
}

// Parse a single CSV line (handles quoted fields)
function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            values.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }

    values.push(current.trim());
    return values;
}

// Load portfolio from file (for local testing)
function loadPortfolioFromFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            portfolioData = JSON.parse(e.target.result);
            loadDashboard();
        } catch (error) {
            alert('Error loading portfolio file: ' + error.message);
        }
    };
    reader.readAsText(file);
}

// Merge portfolio data - combines existing and imported data
function mergePortfolioData(existing, imported) {
    console.log('=== Merging Portfolio Data ===');
    console.log('Existing accounts:', Object.keys(existing.accounts).length);
    console.log('Imported accounts:', Object.keys(imported.accounts).length);

    // Create a deep copy of existing data
    const merged = {
        portfolio_name: existing.portfolio_name || imported.portfolio_name,
        created_date: existing.created_date || new Date().toISOString(),
        accounts: JSON.parse(JSON.stringify(existing.accounts))
    };

    // Merge each account from imported data
    for (const pan in imported.accounts) {
        const importedAccount = imported.accounts[pan];

        if (!merged.accounts[pan]) {
            // New account - add it directly
            merged.accounts[pan] = JSON.parse(JSON.stringify(importedAccount));
            console.log(`✓ Added new account: ${pan}`);
        } else {
            // Existing account - merge holdings
            console.log(`→ Merging holdings for account: ${pan}`);

            const existingAccount = merged.accounts[pan];

            // Update account info if available
            if (importedAccount.name) existingAccount.name = importedAccount.name;
            if (importedAccount.email) existingAccount.email = importedAccount.email;

            // Merge holdings
            for (const importedHolding of importedAccount.holdings) {
                // Find if this holding already exists (match by scheme_code or scheme_name)
                const existingIndex = existingAccount.holdings.findIndex(h =>
                    (h.scheme_code && h.scheme_code === importedHolding.scheme_code) ||
                    (h.scheme_name && h.scheme_name === importedHolding.scheme_name)
                );

                if (existingIndex >= 0) {
                    // Update existing holding
                    existingAccount.holdings[existingIndex] = {
                        ...existingAccount.holdings[existingIndex],
                        ...importedHolding
                    };
                    console.log(`  ✓ Updated holding: ${importedHolding.scheme_name}`);
                } else {
                    // Add new holding
                    existingAccount.holdings.push(JSON.parse(JSON.stringify(importedHolding)));
                    console.log(`  ✓ Added new holding: ${importedHolding.scheme_name}`);
                }
            }
        }
    }

    console.log('=== Merge Complete ===');
    console.log('Total accounts after merge:', Object.keys(merged.accounts).length);

    let totalHoldings = 0;
    for (const pan in merged.accounts) {
        totalHoldings += merged.accounts[pan].holdings.length;
    }
    console.log('Total holdings after merge:', totalHoldings);

    return merged;
}

// Update PAN filter dropdown
function updatePanFilter() {
    const panFilter = document.getElementById('panFilter');
    const currentValue = panFilter.value;

    // Clear existing options except "All"
    panFilter.innerHTML = '<option value="">All Accounts</option>';

    // Add option for each PAN
    for (const pan in portfolioData.accounts) {
        const account = portfolioData.accounts[pan];
        const option = document.createElement('option');
        option.value = pan;
        option.textContent = `${pan} - ${account.name}`;
        panFilter.appendChild(option);
    }

    // Restore previous selection if it still exists
    if (currentValue && portfolioData.accounts[currentValue]) {
        panFilter.value = currentValue;
    }
}

// Apply filters to holdings table
function applyFilters() {
    const panFilter = document.getElementById('panFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const searchText = document.getElementById('searchInput').value.toLowerCase();

    const rows = document.querySelectorAll('#holdingsTableBody tr');

    rows.forEach(row => {
        const pan = row.getAttribute('data-pan');
        const category = row.getAttribute('data-category');
        const text = row.textContent.toLowerCase();

        let show = true;

        // Apply PAN filter
        if (panFilter && pan !== panFilter) {
            show = false;
        }

        // Apply category filter
        if (categoryFilter && category !== categoryFilter) {
            show = false;
        }

        // Apply search filter
        if (searchText && !text.includes(searchText)) {
            show = false;
        }

        row.style.display = show ? '' : 'none';
    });
}

// Clear all filters
function clearFilters() {
    document.getElementById('panFilter').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('searchInput').value = '';
    applyFilters();
}

// Edit holding
function editHolding(pan, index) {
    const holding = portfolioData.accounts[pan].holdings[index];

    // Populate form
    document.getElementById('editPan').value = pan;
    document.getElementById('editIndex').value = index;
    document.getElementById('editSchemeName').value = holding.scheme_name;
    document.getElementById('editUnits').value = holding.units;
    document.getElementById('editInvested').value = holding.invested;
    document.getElementById('editCurrentNav').value = holding.current_nav;
    document.getElementById('editCurrentValue').value = holding.current_value;
    document.getElementById('editCategory').value = holding.category || '';
    document.getElementById('editFolio').value = holding.folio || '';

    // Show modal
    document.getElementById('editModal').style.display = 'block';
}

// Save edited holding
function saveEditedHolding(e) {
    e.preventDefault();

    const pan = document.getElementById('editPan').value;
    const index = parseInt(document.getElementById('editIndex').value);

    const holding = portfolioData.accounts[pan].holdings[index];

    // Update values
    holding.units = parseFloat(document.getElementById('editUnits').value);
    holding.invested = parseFloat(document.getElementById('editInvested').value);
    holding.current_nav = parseFloat(document.getElementById('editCurrentNav').value);
    holding.current_value = parseFloat(document.getElementById('editCurrentValue').value);
    holding.category = document.getElementById('editCategory').value;
    holding.folio = document.getElementById('editFolio').value;

    // Refresh dashboard
    loadDashboard();

    // Close modal
    document.getElementById('editModal').style.display = 'none';

    // Show success message
    console.log('✓ Holding updated successfully');
}

// Delete holding
function deleteHolding(pan, index) {
    const holding = portfolioData.accounts[pan].holdings[index];

    if (confirm(`Are you sure you want to delete "${holding.scheme_name}"?\n\nThis action cannot be undone.`)) {
        // Remove holding
        portfolioData.accounts[pan].holdings.splice(index, 1);

        // If account has no more holdings, optionally remove the account
        if (portfolioData.accounts[pan].holdings.length === 0) {
            if (confirm(`Account ${pan} now has no holdings. Do you want to remove this account?`)) {
                delete portfolioData.accounts[pan];
            }
        }

        // Refresh dashboard
        loadDashboard();

        console.log('✓ Holding deleted successfully');
    }
}

// Setup event listeners for new features
function setupNewFeatureListeners() {
    // Filter listeners
    document.getElementById('panFilter').addEventListener('change', applyFilters);
    document.getElementById('categoryFilter').addEventListener('change', applyFilters);
    document.getElementById('clearFilters').addEventListener('click', clearFilters);

    // Search with filters
    const oldSearchInput = document.getElementById('searchInput');
    oldSearchInput.removeEventListener('keyup', oldSearchInput);
    oldSearchInput.addEventListener('keyup', applyFilters);

    // Edit modal close
    document.querySelectorAll('.close-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            document.getElementById('editModal').style.display = 'none';
        });
    });

    // Edit form submit
    document.getElementById('editHoldingForm').addEventListener('submit', saveEditedHolding);

    // Close modal on outside click
    window.addEventListener('click', function(event) {
        const editModal = document.getElementById('editModal');
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    });

    // Delegate edit/delete button clicks
    document.getElementById('holdingsTableBody').addEventListener('click', function(e) {
        const editBtn = e.target.closest('.btn-edit');
        const deleteBtn = e.target.closest('.btn-delete');

        if (editBtn) {
            const pan = editBtn.getAttribute('data-pan');
            const index = parseInt(editBtn.getAttribute('data-index'));
            editHolding(pan, index);
        }

        if (deleteBtn) {
            const pan = deleteBtn.getAttribute('data-pan');
            const index = parseInt(deleteBtn.getAttribute('data-index'));
            deleteHolding(pan, index);
        }
    });
}

// Initialize new features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupNewFeatureListeners();
});
