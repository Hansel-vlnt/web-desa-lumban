// ============================================
// MAIN JAVASCRIPT
// ============================================

$(document).ready(function() {
    // Initialize AOS
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });

    // Smooth scroll for anchor links
    $('a[href^="#"]').on('click', function(e) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 800);
        }
    });

    // Auto-dismiss alerts
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Review form submission
    $('#reviewForm').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    $('#reviewModal .modal-body').html(`
                        <div class="text-center py-4">
                            <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                            <h5>Review Berhasil Dikirim!</h5>
                            <p>Kode OTP Anda: <strong>${response.otp}</strong></p>
                            <div class="input-group mt-3">
                                <input type="text" id="otpInput" class="form-control" placeholder="Masukkan OTP" maxlength="6">
                                <button class="btn btn-primary" onclick="verifyOTP(${response.review_id})">
                                    <i class="fas fa-check"></i> Verifikasi
                                </button>
                            </div>
                            <div id="otpResult" class="mt-2"></div>
                        </div>
                    `);
                    $('#reviewModal').modal('show');
                } else {
                    alert('Error: ' + response.error);
                }
            },
            error: function() {
                alert('Terjadi kesalahan. Silakan coba lagi.');
            }
        });
    });
});

// Verify OTP
function verifyOTP(reviewId) {
    var otp = $('#otpInput').val();
    if (!otp || otp.length !== 6) {
        $('#otpResult').html('<div class="alert alert-danger">Masukkan 6 digit OTP</div>');
        return;
    }
    
    $.ajax({
        url: '/review/verify',
        type: 'POST',
        data: {
            review_id: reviewId,
            otp: otp
        },
        success: function(response) {
            if (response.success) {
                $('#otpResult').html('<div class="alert alert-success">✅ ' + response.message + '</div>');
                setTimeout(function() {
                    $('#reviewModal').modal('hide');
                    location.reload();
                }, 2000);
            } else {
                $('#otpResult').html('<div class="alert alert-danger">❌ ' + response.error + '</div>');
            }
        },
        error: function() {
            $('#otpResult').html('<div class="alert alert-danger">Terjadi kesalahan. Silakan coba lagi.</div>');
        }
    });
}

// Search functionality
function searchPlaces(query) {
    if (query.length < 2) {
        $('#searchResults').hide();
        return;
    }
    
    $.ajax({
        url: '/api/places/search?q=' + encodeURIComponent(query),
        type: 'GET',
        success: function(results) {
            if (results.length > 0) {
                var html = '<div class="list-group">';
                results.forEach(function(place) {
                    html += `<a href="/wisata/${place.slug}" class="list-group-item list-group-item-action">
                                <i class="fas fa-map-marker-alt text-primary"></i> 
                                ${place.name}
                                <span class="badge bg-secondary float-end">${place.category}</span>
                            </a>`;
                });
                html += '</div>';
                $('#searchResults').html(html).show();
            } else {
                $('#searchResults').html('<div class="text-muted p-3">Tidak ditemukan</div>').show();
            }
        }
    });
}

// Print QR Code
function printQR() {
    window.print();
}

// Share functionality
function shareULOS(name, url) {
    if (navigator.share) {
        navigator.share({
            title: name,
            text: `Lihat ${name} - Warisan Budaya Batak Toba`,
            url: url
        }).catch(() => {});
    } else {
        navigator.clipboard.writeText(url).then(function() {
            alert('Link berhasil disalin!');
        });
    }
}