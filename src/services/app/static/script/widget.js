"use strict";
window.addEventListener('load', () => {
    for (let widget of document.getElementsByTagName('discord-widget')) {
        //getting attributes
        let id = widget.getAttribute('id') ?? null;
        let width = widget.getAttribute('width') ?? '350px';
        let height = widget.getAttribute('height') ?? '500px';
        let footerText = widget.getAttribute('footerText') ?? '';
        let color = widget.getAttribute('color') ?? '#5865f2';
        let backgroundColor = widget.getAttribute('backgroundColor') ?? '#0c0c0d';
        let textColor = widget.getAttribute('textColor') ?? '#fff';
        let statusColor = widget.getAttribute('statusColor') ?? '#858585';
        if (!id) {
            console.error(`${widget.outerHTML}, No Discord server ID specified.`);
        }
        //header
        let head = document.createElement('widget-header');
        let logo = document.createElement('widget-logo');
        let count = document.createElement('widget-header-count');
        head.append(logo, count);
        //footer
        let body = document.createElement('widget-body');
        //footer
        let footer = document.createElement('widget-footer');
        let footerInfo = document.createElement('widget-footer-info');
        let joinButton = document.createElement('widget-button-join');
        joinButton.addEventListener('click', e => {
            if (joinButton.getAttribute('href')) {
                window.open(joinButton.getAttribute('href') || '', joinButton.getAttribute('target') || '', '');
            }
        });
        footerInfo.innerText = footerText;
        joinButton.innerText = 'Join';
        footer.append(footerInfo, joinButton);
        //style
        widget.innerHTML = '<link rel="stylesheet" href="lock/css/discordWidget.css">';
        widget.style.height = height;
        widget.style.width = width;
        widget.style.setProperty("--color", color);
        widget.style.setProperty("--bgColor", backgroundColor);
        widget.style.setProperty("--textColor", textColor);
        widget.style.setProperty("--buttonColor", `#${LDColor(color.replace('#', ''), -10)}`);
        widget.style.setProperty("--statusColor", statusColor);
        //appending head, body and footer to the widget
        widget.append(head, body, footer);
        //data
        fetch(`https://discord.com/api/guilds/${id}/widget.json`).then(data => {
            data.json().then(data => {
                //member count
                //count.innerHTML = `<div class="text-dark"><strong>${data.presence_count - 1}</strong> в сети</div>`;
                //join button
                joinButton.setAttribute('href', data.instant_invite);
                joinButton.setAttribute('target', '_blank');
                //users
                data.members.forEach((user) => {
                    let member = document.createElement('widget-member');
                    let avatar = document.createElement('widget-member-avatar');
                    let avatarIMG = document.createElement('img');
                    let status = document.createElement(`widget-member-status-${user.status}`);
                    let name = document.createElement('widget-member-name');
                    let statusText = document.createElement('widget-member-status-text');
                    avatarIMG.src = user.avatar_url;
                    status.classList.add('widget-member-status');
                    name.innerText = user.username;
                    if (user.game) {
                        statusText.innerText = user.game.name;
                    }
                    avatar.append(avatarIMG, status);
                    member.append(avatar, name, statusText);
                    body.append(member);
                });
            });
        });
    }
});
function LDColor(color, percent) {
    let num = parseInt(color, 16);
    let amt = Math.round(2.55 * percent);
    let R = (num >> 16) + amt;
    let B = (num >> 8 & 0x00FF) + amt;
    let G = (num & 0x0000FF) + amt;
    return (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (B < 255 ? B < 1 ? 0 : B : 255) * 0x100 + (G < 255 ? G < 1 ? 0 : G : 255)).toString(16).slice(1);
}
;
