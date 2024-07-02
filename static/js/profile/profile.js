document.addEventListener("DOMContentLoaded", function () {
            const friendButtons = document.querySelectorAll(".friends__button");

            friendButtons.forEach(button => {
                button.addEventListener("click", function () {
                    const profilePicture = this.getAttribute("data-friend-profile-picture");
                    const city = this.getAttribute("data-friend-city");
                    const name = this.getAttribute("data-friend-name");
                    const surname = this.getAttribute("data-friend-surname");
                    const instagram = this.getAttribute("data-friend-instagram");
                    const tiktok = this.getAttribute("data-friend-tiktok");
                    const phoneNumber = this.getAttribute("data-friend-phone");

                    const profilePictureElement = document.getElementById("friend-profile-picture");
                    const locationElement = document.getElementById("friend-location");
                    const nameElement = document.getElementById("friend-name");
                    const instagramElement = document.getElementById("friend-instagram");
                    const tiktokElement = document.getElementById("friend-tiktok");
                    const phoneElement = document.getElementById("friend-phone");

                    if (profilePictureElement && locationElement && nameElement && instagramElement && tiktokElement && phoneElement) {
                        profilePictureElement.src = profilePicture || "{% static 'image/photo.png' %}";
                        locationElement.textContent = city;
                        nameElement.innerHTML = `${name}<br />${surname}`;
                        instagramElement.href = "https://www.instagram.com/" + instagram || "#";
                        tiktokElement.href = "https://www.tiktok.com/" + tiktok || "#";
                        phoneElement.href = `tel:${phoneNumber || 'N/A'}`;
                        phoneElement.textContent = phoneNumber || '+7 700 100 01 10';

                        document.querySelector(".popup.friend").classList.add("popup--active");
                        document.body.classList.add("body--overflow");
                    }
                });
            });

            const popupCloseButtons = document.querySelectorAll(".popup-close");
            popupCloseButtons.forEach(button => {
                button.addEventListener("click", function () {
                    const index = this.getAttribute("data-index");
                    document.querySelector(`.popup[data-index="${index}"]`).classList.remove("popup--active");
                    document.body.classList.remove("body--overflow");
                });
            });
        });


